import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Trash2, Calendar, Play } from 'lucide-react';
import { Video } from '../../types';
import Modal from '../UI/Modal';

interface VideoCardProps {
  video: Video;
  onDelete: (videoId: string) => void;
}

const VideoCard: React.FC<VideoCardProps> = ({ video, onDelete }) => {
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = () => {
    onDelete(video.id);
    setShowDeleteModal(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <>
      <Link to={`/video/${video.id}`}>
        <div className="card p-4 group cursor-pointer">
          <div className="relative mb-3">
            <img
              src={'https://images.pexels.com/photos/1040160/pexels-photo-1040160.jpeg?auto=compress&cs=tinysrgb&w=400'}
              alt={video.display_title}
              className="w-full h-48 object-cover rounded-lg"
            />
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200 rounded-lg flex items-center justify-center">
              <Play className="w-12 h-12 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
            </div>
          </div>
          
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="font-medium text-gray-900 line-clamp-2 mb-1">
                {video.display_title}
              </h3>
              <div className="flex items-center text-sm text-gray-500">
                <Calendar className="w-4 h-4 mr-1" />
                {formatDate(video.uploaded_at)}
              </div>
            </div>
            
            <button
              onClick={handleDeleteClick}
              className="ml-2 p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </Link>

      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete Video"
      >
        <div className="space-y-4">
          <p className="text-gray-700">
            Are you sure you want to delete "<strong>{video.title}</strong>"? This action cannot be undone.
          </p>
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setShowDeleteModal(false)}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleDeleteConfirm}
              className="btn-danger"
            >
              Delete Video
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
};

export default VideoCard;