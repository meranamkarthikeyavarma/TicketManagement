import React, { useState } from 'react';
import { MoreVertical, MessageSquare, AlertCircle, ArrowRight, Trash2 } from 'lucide-react';

interface Ticket {
  id: string;
  title: string;
  description: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  status: 'OPEN' | 'IN_PROGRESS' | 'CLOSED';
  reporter: string;
  commentCount: number;
}

interface TicketCardProps {
  ticket: Ticket;
  onUpdate: (ticketId: string, updates: any) => void;
  onDelete: (ticketId: string) => void;
  onOpenDetail: (ticket: Ticket) => void;
}

const TicketCard: React.FC<TicketCardProps> = ({ ticket, onUpdate, onDelete, onOpenDetail }) => {
  const [showMenu, setShowMenu] = useState(false);

  const priorityColors = {
    LOW: 'bg-blue-100 text-blue-700',
    MEDIUM: 'bg-yellow-100 text-yellow-700',
    HIGH: 'bg-red-100 text-red-700'
  };

  const handleMoveTicket = (newStatus: string) => {
    onUpdate(ticket.id, { status: newStatus });
    setShowMenu(false);
  };

  const handleCardClick = (e: React.MouseEvent) => {
    // Don't open detail if clicking on the menu button or menu itself
    if ((e.target as HTMLElement).closest('.menu-button') || 
        (e.target as HTMLElement).closest('.menu-dropdown')) {
      return;
    }
    onOpenDetail(ticket);
  };

  return (
    <div 
      className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition relative cursor-pointer"
      onClick={handleCardClick}
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-medium text-gray-800 flex-1 pr-2">{ticket.title}</h3>
        <div className="relative menu-button">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowMenu(!showMenu);
            }}
            className="p-1 hover:bg-gray-100 rounded transition"
          >
            <MoreVertical size={18} className="text-gray-600" />
          </button>

          {showMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowMenu(false);
                }}
              ></div>
              <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20 menu-dropdown">
                            {/* Only show forward movement options */}
              {ticket.status === 'OPEN' && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleMoveTicket('IN_PROGRESS');
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center gap-2"
                >
                  <ArrowRight size={16} />
                  <span>Move to In Progress</span>
                </button>
              )}

              {ticket.status === 'IN_PROGRESS' && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleMoveTicket('CLOSED');
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-center gap-2"
                >
                  <ArrowRight size={16} />
                  <span>Move to Done</span>
                </button>
              )}

              {/* No move option for CLOSED status - it's the final state */}
                <div className="border-t border-gray-200 my-1"></div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(ticket.id);
                    setShowMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-red-50 text-red-600 flex items-center gap-2"
                >
                  <Trash2 size={16} />
                  <span>Delete</span>
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      <p className="text-sm text-gray-600 mb-3 line-clamp-2">{ticket.description}</p>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${priorityColors[ticket.priority]}`}>
            {ticket.priority}
          </span>
        </div>
        
        {ticket.commentCount > 0 && (
          <div className="flex items-center gap-1 text-gray-500 text-sm">
            <MessageSquare size={16} />
            <span>{ticket.commentCount}</span>
          </div>
        )}
      </div>

      <div className="mt-3 pt-3 border-t border-gray-100">
        <p className="text-xs text-gray-500">Reporter: {ticket.reporter}</p>
      </div>
    </div>
  );
};

export default TicketCard;