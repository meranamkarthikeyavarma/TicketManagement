import React, { useState, useEffect } from 'react';
import { X, MessageSquare, User, Calendar, Flag } from 'lucide-react';

interface Ticket {
  id: string;
  title: string;
  description: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  status: 'OPEN' | 'IN_PROGRESS' | 'CLOSED';
  reporter: string;
  createdAt: string;
}

interface Comment {
  id: string;
  author: string;
  body: string;
  createdAt: string;
}

interface TicketDetailModalProps {
  ticket: Ticket;
  onClose: () => void;
  currentUser: string;
}

const TicketDetailModal: React.FC<TicketDetailModalProps> = ({ ticket, onClose, currentUser: _currentUser  }) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [commentAuthor, setCommentAuthor] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [ticket.id]);

  const fetchComments = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/tickets/${ticket.id}/comments`);
      const data = await response.json();
      setComments(data || []);
    } catch (error) {
      console.error('Error fetching comments:', error);
    } finally {
      setLoading(false);
    }
  };
const handleAddComment = async () => {
  if (!newComment.trim() || !commentAuthor.trim()) return;  // ✅ Check both fields

  setSubmitting(true);
  try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/tickets/${ticket.id}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        author: commentAuthor.trim(),  // ✅ Use commentAuthor instead of currentUser
        body: newComment.trim()
      })
    });

    if (response.ok) {
      setNewComment('');
      setCommentAuthor('');  // ✅ Clear the author field too
      fetchComments();
    }

    } catch (error) {
      console.error('Error adding comment:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const priorityColors = {
    LOW: 'bg-blue-100 text-blue-700 border-blue-200',
    MEDIUM: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    HIGH: 'bg-red-100 text-red-700 border-red-200'
  };

  const statusLabels = {
    OPEN: 'Backlog',
    IN_PROGRESS: 'In Progress',
    CLOSED: 'Done'
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  const formatCommentTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return formatDate(dateString);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">{ticket.title}</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content - Left Side */}
            <div className="lg:col-span-2 space-y-6">
              {/* Description */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Description</h3>
                <p className="text-gray-600 whitespace-pre-wrap">{ticket.description}</p>
              </div>

              {/* Comments Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                  <MessageSquare size={20} />
                  Comments ({comments.length})
                </h3>

                {/* Comments List */}
                <div className="space-y-4 mb-4">
                  {loading ? (
                    <div className="text-center py-8">
                      <div className="inline-block w-6 h-6 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                  ) : comments.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">No comments yet. Be the first to comment!</p>
                  ) : (
                    comments.map((comment) => (
                      <div key={comment.id} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                          <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                            <User size={16} className="text-indigo-600" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-gray-800">{comment.author}</span>
                              <span className="text-xs text-gray-500">{formatCommentTime(comment.createdAt)}</span>
                            </div>
                            <p className="text-gray-700">{comment.body}</p>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Add Comment Input */}
                <div className="space-y-3">
                                    <input
                    type="text"
                    value={commentAuthor}
                    onChange={(e) => setCommentAuthor(e.target.value)}
                    placeholder="Your name"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                    disabled={submitting}
                />
                                <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Add a comment..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none resize-none"
                    rows={3}
                    disabled={submitting}
                    
                  />
                  <div className="flex justify-end">
                <button
                onClick={handleAddComment}
                disabled={submitting || !newComment.trim() || !commentAuthor.trim()}  // ✅ Update this condition
                className="..."
                >
                                {submitting ? 'Posting...' : 'Post Comment'}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Sidebar - Right Side */}
            <div className="space-y-4">
              {/* Status */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <Flag size={16} />
                  <span className="text-sm font-medium">Status</span>
                </div>
                <div className="text-gray-800 font-medium">{statusLabels[ticket.status]}</div>
              </div>

              {/* Assignee */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <User size={16} />
                  <span className="text-sm font-medium">Assignee</span>
                </div>
                <div className="text-gray-800 font-medium">{ticket.reporter}</div>
              </div>

              {/* Priority */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <Flag size={16} />
                  <span className="text-sm font-medium">Priority</span>
                </div>
                <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium border ${priorityColors[ticket.priority]}`}>
                  {ticket.priority}
                </span>
              </div>

              {/* Dates */}
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <Calendar size={16} />
                  <span className="text-sm font-medium">Dates</span>
                </div>
                <div className="text-sm text-gray-600">
                  <div>Created: {formatDate(ticket.createdAt)}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TicketDetailModal;
