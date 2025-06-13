import axios from 'axios';

interface LogEntry {
  message: string;
  data?: unknown;
}

const isDevEnvironment = import.meta.env.DEV;

const formatLog = (level: 'log' | 'warn' | 'error', entry: LogEntry): void => {
  if (!isDevEnvironment) {
    return;
  }

  let output = `[${level.toUpperCase()}] ${entry.message}`;
  
  if (entry.data) {
    if (axios.isAxiosError(entry.data)) {
      const { message, code, response } = entry.data;
      const simplifiedError = {
        message,
        code,
        status: response?.status,
        statusText: response?.statusText,
        data: response?.data, // Be cautious with this in real-world scenarios
      };
      output += `\nAxios Error: ${JSON.stringify(simplifiedError, null, 2)}`;
    } else if (entry.data instanceof Error) {
      output += `\nError: ${entry.data.message}\nStack: ${entry.data.stack}`;
    } else {
      try {
        output += `\nData: ${JSON.stringify(entry.data, null, 2)}`;
      } catch {
        output += `\nData: [Unserializable]`;
      }
    }
  }

  switch (level) {
    case 'log':
      console.log(output);
      break;
    case 'warn':
      console.warn(output);
      break;
    case 'error':
      console.error(output);
      break;
  }
};

export const logger = {
  log: (message: string, data?: unknown): void => {
    formatLog('log', { message, data });
  },
  warn: (message: string, data?: unknown): void => {
    formatLog('warn', { message, data });
  },
  error: (message: string, data?: unknown): void => {
    formatLog('error', { message, data });
  },
}; 