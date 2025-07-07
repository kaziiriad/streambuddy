import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from '../api/axios';
import { Video, VideoContextType } from '../types';
import { useAuth } from './AuthContext';

const VideoContext = createContext<VideoContextType | undefined>(undefined);

export const useVideo = () => {
  const context = useContext(VideoContext);
  if (context === undefined) {
    throw new Error('useVideo must be used within a VideoProvider');
  }
  return context;
};

interface VideoProviderProps {
  children: ReactNode;
}

export const VideoProvider: React.FC<VideoProviderProps> = ({ children }) => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      loadVideos();
    }
  }, [user]);

  const loadVideos = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('/api/videos/');
      if (Array.isArray(response.data)) {
        setVideos(response.data);
      } else {
        setVideos([]); // Ensure videos is always an array
      }
    } catch (error) {
      console.error('Failed to load videos:', error);
      setVideos([]); // Also ensure it's an array on error
    } finally {
      setIsLoading(false);
    }
  };

  const uploadVideo = async (file: File): Promise<void> => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', file.name.replace(/\.[^/.]+$/, '')); // Use filename as title
      await axios.post('/api/videos/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      await loadVideos(); // Refresh the video list
    } catch (error) {
      throw new Error('Upload failed');
    } finally {
      setIsLoading(false);
    }
  };

  const deleteVideo = async (videoId: string): Promise<void> => {
    setIsLoading(true);
    try {
      const video = videos.find(v => v.id === videoId);
      if (video) {
        await axios.delete(`/api/videos/${video.title}/`);
        await loadVideos(); // Refresh the video list
      }
    } catch (error) {
      throw new Error('Delete failed');
    } finally {
      setIsLoading(false);
    }
  };

  const getVideo = (videoId: string): Video | undefined => {
    return videos.find(video => video.id === videoId);
  };

  const value: VideoContextType = {
    videos,
    uploadVideo,
    deleteVideo,
    getVideo,
    isLoading,
  };

  return (
    <VideoContext.Provider value={value}>
      {children}
    </VideoContext.Provider>
  );
};