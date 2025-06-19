import axios from 'axios';

interface LogEntry {
  message: string;
  data?: unknown;
}

const isDevEnvironment = import.meta.env.DEV;

// Safe serialization to prevent circular references
const safeStringify = (obj: unknown, maxDepth = 3): string => {
  const seen = new WeakSet();
  
  const stringify = (value: unknown, depth = 0): unknown => {
    if (depth > maxDepth) return '[Max Depth Reached]';
    
    if (value === null || value === undefined) return value;
    
    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
      return value;
    }
    
    if (value instanceof Error) {
      return {
        name: value.name,
        message: value.message,
        stack: value.stack?.substring(0, 500) // Limit stack trace length
      };
    }
    
    if (typeof value === 'object') {
      if (seen.has(value as object)) {
        return '[Circular Reference]';
      }
      
      seen.add(value as object);
      
      if (Array.isArray(value)) {
        return value.slice(0, 10).map(item => stringify(item, depth + 1)); // Limit array size
      }
      
      const result: Record<string, unknown> = {};
      const entries = Object.entries(value as Record<string, unknown>).slice(0, 20); // Limit object properties
      
      for (const [key, val] of entries) {
        try {
          result[key] = stringify(val, depth + 1);
        } catch {
          result[key] = '[Unserializable]';
        }
      }
      
      return result;
    }
    
    return '[Unserializable Type]';
  };
  
  try {
    return JSON.stringify(stringify(obj), null, 2);
  } catch {
    return '[Serialization Failed]';
  }
};

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
        // Only include essential response data to prevent circular references
        data: response?.data ? (typeof response.data === 'string' ? response.data.substring(0, 500) : '[Response Data]') : undefined,
      };
      output += `\nAxios Error: ${safeStringify(simplifiedError)}`;
    } else if (entry.data instanceof Error) {
      output += `\nError: ${entry.data.message}\nStack: ${entry.data.stack?.substring(0, 500) || 'No stack trace'}`;
    } else {
      output += `\nData: ${safeStringify(entry.data)}`;
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
  info: (message: string, data?: unknown): void => {
    formatLog('log', { message, data });
  }
}; 