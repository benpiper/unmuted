import { alpha } from '@mui/material/styles';

const getDesignTokens = (mode) => ({
  palette: {
    mode,
    ...(mode === 'light'
      ? {
          // palette values for light mode
          primary: {
            main: '#2563eb',
          },
          background: {
            default: '#f8fafc',
            paper: '#ffffff',
          },
          text: {
            primary: '#1e293b',
            secondary: '#64748b',
          },
          // Custom variables
          customMedia: {
            bg: 'rgba(0, 0, 0, 0.04)',
            border: 'rgba(0, 0, 0, 0.08)',
          },
          customTimeline: {
            bg: 'rgba(0, 0, 0, 0.02)',
          },
          customCandidate: {
            bg: 'rgba(0, 0, 0, 0.03)',
            selected: 'rgba(37, 99, 235, 0.15)',
          },
          customInfo: {
            bg: 'rgba(37, 99, 235, 0.08)',
          },
          customAccent: {
            shadow: 'rgba(37, 99, 235, 0.15)',
            shadowHover: 'rgba(37, 99, 235, 0.25)',
            gradient: 'linear-gradient(135deg, #2563eb, #7c3aed)',
          }
        }
      : {
          // palette values for dark mode
          primary: {
            main: '#3b82f6',
          },
          background: {
            default: '#0c0d11',
            paper: 'rgba(255, 255, 255, 0.03)',
          },
          text: {
            primary: '#f0f0f0',
            secondary: '#9ca3af',
          },
          // Custom variables
          customMedia: {
            bg: 'rgba(0, 0, 0, 0.3)',
            border: 'rgba(255, 255, 255, 0.1)',
          },
          customTimeline: {
            bg: 'rgba(0, 0, 0, 0.2)',
          },
          customCandidate: {
            bg: 'rgba(255, 255, 255, 0.05)',
            selected: 'rgba(59, 130, 246, 0.3)',
          },
          customInfo: {
            bg: 'rgba(59, 130, 246, 0.1)',
          },
          customAccent: {
            shadow: 'rgba(59, 130, 246, 0.3)',
            shadowHover: 'rgba(59, 130, 246, 0.4)',
            gradient: 'linear-gradient(135deg, #60a5fa, #a78bfa)',
          }
        }),
  },
  typography: {
    fontFamily: '"Outfit", "Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 800,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: () => ({
          backgroundColor: mode === 'dark' ? 'rgba(255, 255, 255, 0.03)' : '#ffffff',
          backdropFilter: 'blur(12px)',
          borderRadius: '20px',
          border: `1px solid ${mode === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'}`,
          boxShadow: mode === 'dark' ? '0 12px 40px rgba(0,0,0,0.4)' : '0 10px 30px rgba(0,0,0,0.08)',
          backgroundImage: 'none',
        }),
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '10px',
          textTransform: 'none',
          fontWeight: 600,
          padding: '0.8rem 1.5rem',
        },
        containedPrimary: ({ theme }) => ({
          boxShadow: `0 4px 14px ${alpha(theme.palette.primary.main, 0.3)}`,
          '&:hover': {
            boxShadow: `0 6px 20px ${alpha(theme.palette.primary.main, 0.4)}`,
          },
        }),
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: ({ theme }) => ({
          '& .MuiOutlinedInput-root': {
            borderRadius: '10px',
            backgroundColor: mode === 'dark' ? 'rgba(0, 0, 0, 0.25)' : 'rgba(255, 255, 255, 0.7)',
            '& fieldset': {
              borderColor: mode === 'dark' ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)',
            },
            '&:hover fieldset': {
              borderColor: theme.palette.primary.main,
            },
          },
        }),
      },
    },
  },
});

export default getDesignTokens;
