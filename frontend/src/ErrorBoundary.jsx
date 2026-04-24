import React from 'react';
import { Box, Container, Paper, Typography, Button } from '@mui/material';
import { RestartAlt as RestartIcon } from '@mui/icons-material';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
          <Container maxWidth="sm">
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h5" sx={{ fontWeight: 700, mb: 2, color: 'error.main' }}>
                ⚠️ Something went wrong
              </Typography>
              <Typography variant="body2" sx={{ mb: 3, color: 'textSecondary' }}>
                An unexpected error occurred. Please try refreshing the page or contact support if the problem persists.
              </Typography>
              {import.meta.env.DEV && this.state.error && (
                <Box sx={{ mb: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider', textAlign: 'left' }}>
                  <Typography variant="caption" sx={{ fontFamily: 'monospace', fontSize: '0.7rem', wordBreak: 'break-word' }}>
                    {this.state.error.toString()}
                  </Typography>
                </Box>
              )}
              <Button
                variant="contained"
                startIcon={<RestartIcon />}
                onClick={this.handleReset}
              >
                Try Again
              </Button>
            </Paper>
          </Container>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
