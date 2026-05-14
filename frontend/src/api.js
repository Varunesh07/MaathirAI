import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

export const fetchMemory = async () => {
  try {
    const res = await api.get('/interactions/memory');
    return {
      ...res.data.medical_profile,
      interactions: res.data.interactions || []
    };
  } catch (err) {
    console.error("Error fetching memory:", err);
    return null;
  }
};

export const fetchChatHistory = async () => {
  try {
    const res = await api.get('/chat/');
    return res.data.chat_history;
  } catch (err) {
    console.error("Error fetching chat history:", err);
    return [];
  }
};

export const clearMemory = async () => {
  await api.delete('/interactions/memory');
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('files', file); 
  const res = await api.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export const sendMessage = async (message) => {
  const res = await api.post('/chat/', { message });
  return res.data;
};

export const streamMessage = async (message, onChunk) => {
  const res = await fetch('http://localhost:8000/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });

  if (!res.ok) throw new Error('Network response was not ok');

  const reader = res.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let done = false;

  while (!done) {
    const { value, done: readerDone } = await reader.read();
    done = readerDone;
    if (value) {
      const chunk = decoder.decode(value, { stream: true });
      onChunk(chunk);
    }
  }
};
