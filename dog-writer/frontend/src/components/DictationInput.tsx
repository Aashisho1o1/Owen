import React from 'react';
import { Button, Text, Paper, Group, Loader, Alert } from '@mantine/core';
import { IconMicrophone, IconPlayerStop, IconAlertCircle } from '@tabler/icons-react'; // Example icons
import { useVoice } from '../hooks/useVoice';

interface OrganizedIdeaDisplayProps {
  original_text?: string;
  summary?: string;
  category?: string;
  error?: string;
}

const OrganizedIdeaDisplay: React.FC<OrganizedIdeaDisplayProps> = ({ original_text, summary, category, error }) => {
  if (error) {
    return <Text c="red">Error organizing idea: {error}</Text>;
  }
  if (!summary && !category && !original_text) {
    return null; // Don't render if no data
  }
  return (
    <Paper shadow="xs" p="md" mt="md" withBorder>
      {original_text && <Text size="sm" c="dimmed">Original: {original_text}</Text>}
      {summary && <Text fw={500}>Summary: {summary}</Text>}
      {category && <Text>Category: {category}</Text>}
    </Paper>
  );
};

export const DictationInput: React.FC = () => {
  const {
    isRecording,
    transcription,
    organizedIdea,
    isLoading,
    error,
    startRecording,
    stopRecording,
    clearError,
    clearTranscription
  } = useVoice();

  const handleToggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      clearTranscription(); // Clear previous results before new recording
      clearError();
      startRecording();
    }
  };

  return (
    <Paper shadow="sm" p="lg" withBorder>
      <Group justify="center">
        <Button 
          onClick={handleToggleRecording} 
          disabled={isLoading && !isRecording} // Disable if loading unless it's to stop current recording
          color={isRecording ? 'red' : 'blue'}
          leftSection={isRecording ? <IconPlayerStop size={18} /> : <IconMicrophone size={18} />}
        >
          {isLoading && isRecording ? 'Processing...' : (isRecording ? 'Stop Dictation' : 'Start Dictation')}
        </Button>
      </Group>

      {isLoading && !isRecording && (
        <Group justify="center" mt="md">
          <Loader size="sm" />
          <Text>Processing audio...</Text>
        </Group>
      )}

      {error && (
        <Alert icon={<IconAlertCircle size="1rem" />} title="Error" color="red" mt="md" withCloseButton onClose={clearError}>
          {error}
        </Alert>
      )}

      {transcription && !isLoading && (
        <Paper shadow="xs" p="md" mt="md" withBorder>
          <Text fw={500}>Transcription:</Text>
          <Text>{transcription}</Text>
        </Paper>
      )}

      {organizedIdea && !isLoading && (
         <OrganizedIdeaDisplay {...organizedIdea} />
      )}
    </Paper>
  );
}; 