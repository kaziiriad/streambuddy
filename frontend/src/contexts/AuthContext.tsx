import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from '../api/axios';
import { User, AuthContextType } from '../types';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on app load
    const storedUser = localStorage.getItem('streambuddy_user');
    const storedToken = localStorage.getItem('streambuddy_token');
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
      axios.defaults.headers.common['Authorization'] = `Token ${storedToken}`;
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    try {
      const response = await axios.post('/api/auth/login/', { email, password });
      const { user, token } = response.data;
      
      setUser(user);
      localStorage.setItem('streambuddy_user', JSON.stringify(user));
      localStorage.setItem('streambuddy_token', token);
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
    } catch (error) {
      throw new Error('Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, confirmPassword: string): Promise<void> => {
    setIsLoading(true);
    try {
      if (password !== confirmPassword) {
        throw new Error('Passwords do not match');
      }
      
      const response = await axios.post('/api/auth/registration/', { email, password, password2: confirmPassword });
      const { user, token } = response.data;

      setUser(user);
      localStorage.setItem('streambuddy_user', JSON.stringify(user));
      localStorage.setItem('streambuddy_token', token);
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
    } catch (error) {
      throw new Error(error instanceof Error ? error.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await axios.post('/api/auth/logout/');
    } catch (error) {
      console.error('Logout failed', error);
    } finally {
      setUser(null);
      localStorage.removeItem('streambuddy_user');
      localStorage.removeItem('streambuddy_token');
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  const value: AuthContextType = {
    user,
    login,
    register,
    logout,
    isLoading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};