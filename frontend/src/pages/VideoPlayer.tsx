import React from 'react';
import { useParams, Link, Navigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import Layout from '../components/Layout/Layout';
import VideoPlayer from '../components/Videos/VideoPlayer';
import { useVideo } from '../contexts/VideoContext';

const VideoPlayerPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { getVideo } = useVideo();

  if (!id) {
    return <Navigate to="/" replace />;
  }

  const video = getVideo(id);

  if (!video) {
    return (
      <Layout>
        <div className="text-center py-12">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Video Not Found</h1>
          <p className="text-gray-600 mb-6">
            The video you're looking for doesn't exist or has been removed.
          </p>
          <Link to="/" className="btn-primary">
            Back to Dashboard
          </Link>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Back Button */}
        <Link
          to="/"
          className="inline-flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors duration-200"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Dashboard</span>
        </Link>

        {/* Video Player */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <VideoPlayer
            dashUrl={video.mpd_file || 'https://dash.akamaized.net/envivio/EnvivioDash3/manifest.mpd'}
            title={video.title}
          />
          
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">Video Details</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Uploaded on {new Date(video.uploaded_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Filename</p>
                <p className="text-sm font-medium text-gray-900">{video.original_filename}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default VideoPlayerPage;