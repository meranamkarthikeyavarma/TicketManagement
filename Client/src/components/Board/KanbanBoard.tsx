import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, LogOut } from 'lucide-react';
import TicketCard from './TicketCard';
import CreateTicketModal from './CreateTicketModal';
import TicketDetailModal from './TicketDetailModal';

interface Ticket {
  id: string;
  title: string;
  description: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  status: 'OPEN' | 'IN_PROGRESS' | 'CLOSED';
  reporter: string;
  assignee?: string;
  commentCount: number;
  createdAt: string;
}

interface KanbanBoardProps {
  user: any;
  onLogout: () => void;
}

const KanbanBoard: React.FC<KanbanBoardProps> = ({ user, onLogout }) => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [activeColumn, setActiveColumn] = useState<'OPEN' | 'IN_PROGRESS' | 'CLOSED' | null>(null);
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);

  useEffect(() => {
    fetchTickets();
    fetchProjectName();
  }, [projectId]);

  const fetchProjectName = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/projects/Project1`);
      const data = await response.json();
      const project = data.projects?.find((p: any) => p.id === projectId);
      if (project) setProjectName(project.name);
    } catch (error) {
      console.error('Error fetching project name:', error);
    }
  };

  const fetchTickets = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/tickets?projectId=${projectId}`);
      const data = await response.json();
      setTickets(data.items || []);
    } catch (error) {
      console.error('Error fetching tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTicket = async (ticketData: any) => {
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/tickets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...ticketData,
          projectId,
          priority: ticketData.priority || 'MEDIUM'
        })
      });

      if (response.ok) {
        fetchTickets();
        setShowCreateModal(false);
      }
    } catch (error) {
      console.error('Error creating ticket:', error);
    }
  };

  const handleUpdateTicket = async (ticketId: string, updates: any) => {
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/tickets/${ticketId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        fetchTickets();
      }
    } catch (error) {
      console.error('Error updating ticket:', error);
    }
  };

  const handleDeleteTicket = async (ticketId: string) => {
    if (!confirm('Are you sure you want to delete this ticket?')) return;

    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/tickets/${ticketId}`, {
        method: 'DELETE'
      });

      if (response.ok || response.status === 204) {
        fetchTickets();
      }
    } catch (error) {
      console.error('Error deleting ticket:', error);
    }
  };

  const handleOpenDetail = (ticket: Ticket) => {
    setSelectedTicket(ticket);
  };

  const handleCloseDetail = () => {
    setSelectedTicket(null);
    // Refresh tickets to update comment counts
    fetchTickets();
  };

  const columns = [
    { id: 'OPEN', title: 'Backlog', color: 'bg-gray-100', textColor: 'text-gray-700' },
    { id: 'IN_PROGRESS', title: 'In progress', color: 'bg-yellow-100', textColor: 'text-yellow-700' },
    { id: 'CLOSED', title: 'Done', color: 'bg-green-100', textColor: 'text-green-700' }
  ];

  const getTicketsByStatus = (status: string) => {
    return tickets.filter(ticket => ticket.status === status);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-2">
            <button
              onClick={() => navigate('/projects')}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-800 transition"
            >
              <ArrowLeft size={20} />
              <span>Back to Projects</span>
            </button>
            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
            >
              <LogOut size={20} />
              <span>Logout</span>
            </button>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">{projectName}</h1>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {columns.map((column) => {
              const columnTickets = getTicketsByStatus(column.id);
              return (
                <div key={column.id} className="bg-gray-100 rounded-xl p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${column.id === 'OPEN' ? 'bg-gray-500' : column.id === 'IN_PROGRESS' ? 'bg-yellow-500' : 'bg-green-500'}`}></div>
                      <h2 className="font-semibold text-gray-800">{column.title}</h2>
                      <span className="text-sm text-gray-600">{columnTickets.length}</span>
                    </div>
                  </div>

                  <div className="space-y-3 mb-3">
                    {columnTickets.map((ticket) => (
                      <TicketCard
                        key={ticket.id}
                        ticket={ticket}
                        onUpdate={handleUpdateTicket}
                        onDelete={handleDeleteTicket}
                        onOpenDetail={handleOpenDetail}
                      />
                    ))}
                                          </div>
                        {column.id === 'OPEN' && (
                          <button
                            onClick={() => {
                              setActiveColumn(column.id as any);
                              setShowCreateModal(true);
                            }}
                            className="w-full flex items-center justify-center gap-2 py-2 text-gray-600 hover:bg-gray-200 rounded-lg transition"
                          >
                            <Plus size={18} />
                            <span>Add item</span>
                          </button>
                        )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create Ticket Modal */}
      {showCreateModal && (
        <CreateTicketModal
          initialStatus={activeColumn || 'OPEN'}
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateTicket}
          reporter={user.name}
        />
      )}

      {/* Ticket Detail Modal */}
      {selectedTicket && (
        <TicketDetailModal
          ticket={selectedTicket}
          onClose={handleCloseDetail}
          currentUser={user}  
        />
      )}
    </div>
  );
};

export default KanbanBoard;
