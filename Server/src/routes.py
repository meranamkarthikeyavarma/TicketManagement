from flask import Blueprint, request, jsonify
from db import get_db, generate_id, row_to_dict
from validators import (
    TicketCreateSchema, 
    TicketUpdateSchema, 
    CommentCreateSchema,
    ProjectCreateSchema
)
from pydantic import ValidationError
from datetime import datetime
from auth import auth_bp

api_bp = Blueprint('api', __name__)

# Register auth routes
# api_bp.register_blueprint(auth_bp)

# ==================== PROJECT ROUTES ====================

@api_bp.route('/projects/<parent_project>', methods=['GET'])
def get_projects(parent_project):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM projects WHERE parentProject = ? ORDER BY createdAt ASC',
            (parent_project,)
        )
        
        projects = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'success': True, 'projects': projects}), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/projects', methods=['POST'])
def create_project():
    try:
        data = ProjectCreateSchema(**request.json)
        
        project_id = generate_id()
        now = datetime.now().isoformat()
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO projects (id, name, parentProject, createdAt) VALUES (?, ?, ?, ?)',
            (project_id, data.name, data.parentProject, now)
        )
        
        conn.commit()
        
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        project = dict(cursor.fetchone())
        conn.close()
        
        return jsonify({'success': True, 'project': project}), 201
    except ValidationError as e:
        return jsonify({'error': e.errors()[0]['msg']}), 422
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Project not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# ==================== TICKET ROUTES ====================

@api_bp.route('/tickets', methods=['POST'])
def create_ticket():
    try:
        data = TicketCreateSchema(**request.json)
        
        ticket_id = generate_id()
        now = datetime.now().isoformat()
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tickets (id, createdAt, updatedAt, title, description, priority, status, reporter, projectId)
            VALUES (?, ?, ?, ?, ?, ?, 'OPEN', ?, ?)
        ''', (ticket_id, now, now, data.title, data.description, data.priority, data.reporter, data.projectId))
        
        conn.commit()
        
        cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        ticket = dict(cursor.fetchone())
        conn.close()
        
        return jsonify(ticket), 201
    except ValidationError as e:
        return jsonify({'issues': [{'message': err['msg']} for err in e.errors()]}), 422
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets', methods=['GET'])
def list_tickets():
    try:
        q = request.args.get('q', '')
        status = request.args.get('status', '')
        project_id = request.args.get('projectId', '')
        
        conn = get_db()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM tickets WHERE 1=1'
        params = []
        
        if project_id:
            # Check if the selected project has sub-projects
            cursor.execute('SELECT id FROM projects WHERE parentProject = ?', (project_id,))
            sub_projects = cursor.fetchall()
            
            if sub_projects:
                # It's a parent project → include all its sub-projects
                sub_project_ids = [row['id'] for row in sub_projects]
                placeholders = ','.join('?' * len(sub_project_ids))
                query += f' AND projectId IN ({placeholders})'
                params.extend(sub_project_ids)
            else:
                # It's a sub-project → fetch normally
                query += ' AND projectId = ?'
                params.append(project_id)
        
        if q:
            query += ' AND (title LIKE ? OR description LIKE ?)'
            params.extend([f'%{q}%', f'%{q}%'])
        
        if status and status != 'ALL':
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY updatedAt DESC'
        
        cursor.execute(query, params)
        tickets = [dict(row) for row in cursor.fetchall()]
        
        # Add comment counts
        tickets_with_counts = []
        for ticket in tickets:
            cursor.execute('SELECT COUNT(*) as count FROM comments WHERE ticketId = ?', (ticket['id'],))
            count = cursor.fetchone()['count']
            ticket['commentCount'] = count
            tickets_with_counts.append(ticket)
        
        conn.close()
        
        return jsonify({'items': tickets_with_counts, 'total': len(tickets_with_counts)}), 200
    except Exception as e:
        print(f'Error fetching tickets: {e}')
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        ticket = cursor.fetchone()
        
        if not ticket:
            conn.close()
            return jsonify({'error': 'Ticket not found'}), 404
        
        ticket = dict(ticket)
        
        cursor.execute('SELECT COUNT(*) as count FROM comments WHERE ticketId = ?', (ticket_id,))
        count = cursor.fetchone()['count']
        ticket['commentCount'] = count
        
        conn.close()
        
        return jsonify(ticket), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets/<ticket_id>', methods=['PATCH'])
def update_ticket(ticket_id):
    try:
        data = TicketUpdateSchema(**request.json)
        now = datetime.now().isoformat()
        
        updates = []
        values = []
        
        if data.title:
            updates.append('title = ?')
            values.append(data.title)
        if data.description:
            updates.append('description = ?')
            values.append(data.description)
        if data.priority:
            updates.append('priority = ?')
            values.append(data.priority)
        if data.status:
            updates.append('status = ?')
            values.append(data.status)
        if data.reporter:
            updates.append('reporter = ?')
            values.append(data.reporter)
        
        if not updates:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        updates.append('updatedAt = ?')
        values.append(now)
        values.append(ticket_id)
        
        query = f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?"
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Ticket not found'}), 404
        
        conn.commit()
        
        cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
        ticket = dict(cursor.fetchone())
        conn.close()
        
        return jsonify(ticket), 200
    except ValidationError as e:
        return jsonify({'issues': [{'message': err['msg']} for err in e.errors()]}), 422
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets/<ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tickets WHERE id = ?', (ticket_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Ticket not found'}), 404
        
        conn.commit()
        conn.close()
        
        return '', 204
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# ==================== COMMENT ROUTES ====================

@api_bp.route('/tickets/<ticket_id>/comments', methods=['POST'])
def add_comment(ticket_id):
    try:
        data = CommentCreateSchema(**request.json)
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if ticket exists
        cursor.execute('SELECT id FROM tickets WHERE id = ?', (ticket_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Ticket not found'}), 404
        
        comment_id = generate_id()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO comments (id, createdAt, author, body, ticketId)
            VALUES (?, ?, ?, ?, ?)
        ''', (comment_id, now, data.author, data.body, ticket_id))
        
        # Update ticket's updatedAt
        cursor.execute('UPDATE tickets SET updatedAt = ? WHERE id = ?', (now, ticket_id))
        
        conn.commit()
        
        cursor.execute('SELECT * FROM comments WHERE id = ?', (comment_id,))
        comment = dict(cursor.fetchone())
        conn.close()
        
        return jsonify(comment), 201
    except ValidationError as e:
        return jsonify({'issues': [{'message': err['msg']} for err in e.errors()]}), 422
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/tickets/<ticket_id>/comments', methods=['GET'])
def list_comments(ticket_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM comments WHERE ticketId = ? ORDER BY createdAt ASC', (ticket_id,))
        comments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(comments), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

# ==================== HEALTH CHECK ====================

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }), 200