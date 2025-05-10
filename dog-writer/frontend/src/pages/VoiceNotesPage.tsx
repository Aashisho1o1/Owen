import React, { useState } from 'react';
import { Container, Title, Paper, Text, Button } from '@mantine/core';
import '../App.css';

// Simplified version without the DictationInput component for debugging
const VoiceNotesPage: React.FC = () => {
  const [error, setError] = useState<string | null>(null);

  return (
    <main className="app-content" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <Container size="md" style={{ width: '100%', paddingTop: '2rem', paddingBottom: '2rem' }}>
        <Paper shadow="md" p="xl" radius="md" withBorder style={{ textAlign: 'center' }}>
          <Title order={1} mb="lg">
            Voice Notes
          </Title>
          <Text c="dimmed" mb="xl">
            Click the button below to start dictating your thoughts and ideas.
            They will be transcribed and organized for you.
          </Text>
          
          {/* Simple button without complex functionality for initial testing */}
          <Button 
            color="blue" 
            size="lg"
            onClick={() => console.log("Voice recording would start here")}
          >
            Start Dictation
          </Button>

          {error && (
            <Text color="red" mt="md">
              {error}
            </Text>
          )}
        </Paper>
      </Container>
    </main>
  );
};

export default VoiceNotesPage; 