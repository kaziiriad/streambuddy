import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost';

const instance = axios.create({
  baseURL,
});

export default instance;
