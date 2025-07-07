import React, { useState } from 'react';
import { Upload, Video } from 'lucide-react';
import Layout from '../components/Layout/Layout';
import VideoCard from '../components/Videos/VideoCard';
import UploadModal from '../components/Videos/UploadModal';
import Loading from '../components/UI/Loading';
import { useVideo } from '../contexts/VideoContext';

const Dashboard: React.FC = () => {
  const [showUploadModal, setShowUploadModal] = useState(false);
  const { videos, deleteVideo, isLoading } = useVideo();

  const handleDeleteVideo = async (videoId: string) => {
    try {
      await deleteVideo(videoId);
    } catch (error) {
      alert('Failed to delete video. Please try again.');
    }
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Your Videos</h1>
            <p className="mt-2 text-gray-600">
              Manage and organize your video content
            </p>
          </div>
          <button
            onClick={() => setShowUploadModal(true)}
            className="mt-4 sm:mt-0 btn-primary flex items-center space-x-2"
          >
            <Upload className="w-5 h-5" />
            <span>Upload Video</span>
          </button>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loading />
          </div>
        ) : videos.length === 0 ? (
          <div className="text-center py-12">
            <Video className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No videos yet
            </h3>
            <p className="text-gray-500 mb-6">
              You haven't uploaded any videos yet. Click 'Upload Video' to get started.
            </p>
            <button
              onClick={() => setShowUploadModal(true)}
              className="btn-primary"
            >
              Upload Your First Video
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {videos.map((video) => (
              <VideoCard
                key={video.id}
                video={video}
                onDelete={handleDeleteVideo}
              />
            ))}
          </div>
        )}
      </div>

      <UploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
      />
    </Layout>
  );
};

export default Dashboard;