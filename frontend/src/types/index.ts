export interface User {
  id: string;
  email: string;
  name?: string;
}

export interface Video {
  id: string;
  title: string;
  display_title: string;
  original_filename: string;
  uploaded_at: string;
  processed: boolean;
  mpd_file?: string;
}

export interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, confirmPassword: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

export interface VideoContextType {
  videos: Video[];
  uploadVideo: (file: File) => Promise<void>;
  deleteVideo: (videoId: string) => Promise<void>;
  getVideo: (videoId: string) => Video | undefined;
  isLoading: boolean;
}