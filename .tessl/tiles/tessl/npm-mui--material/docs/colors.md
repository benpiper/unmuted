# Color System

Material Design color palettes and color manipulation utilities.

## Color Palettes

Material UI provides 20 color palettes following Material Design specifications.

```typescript { .api }
/**
 * Material Design color palettes
 */
const colors: {
  common: CommonColors;
  red: ColorPalette;
  pink: ColorPalette;
  purple: ColorPalette;
  deepPurple: ColorPalette;
  indigo: ColorPalette;
  blue: ColorPalette;
  lightBlue: ColorPalette;
  cyan: ColorPalette;
  teal: ColorPalette;
  green: ColorPalette;
  lightGreen: ColorPalette;
  lime: ColorPalette;
  yellow: ColorPalette;
  amber: ColorPalette;
  orange: ColorPalette;
  deepOrange: ColorPalette;
  brown: ColorPalette;
  grey: ColorPalette;
  blueGrey: ColorPalette;
};

interface CommonColors {
  black: string;
  white: string;
}

interface ColorPalette {
  50: string;
  100: string;
  200: string;
  300: string;
  400: string;
  500: string;
  600: string;
  700: string;
  800: string;
  900: string;
  A100?: string; // Not available for brown, grey, blueGrey
  A200?: string;
  A400?: string;
  A700?: string;
}
```

**Usage Examples:**

```typescript
import { colors } from "@mui/material";
import { red, blue, green } from "@mui/material/colors";

// Using color palettes
const theme = createTheme({
  palette: {
    primary: {
      main: blue[500],
      light: blue[300],
      dark: blue[700],
    },
    secondary: {
      main: red[500],
    },
    error: {
      main: red[600],
    },
    success: {
      main: green[600],
    },
  },
});

// Direct color usage
<Box sx={{ bgcolor: colors.blue[100], color: colors.blue[900] }}>
  Blue themed content
</Box>

// Color variations
<Stack spacing={1}>
  <Box sx={{ bgcolor: red[50], p: 1 }}>Red 50 (lightest)</Box>
  <Box sx={{ bgcolor: red[100], p: 1 }}>Red 100</Box>
  <Box sx={{ bgcolor: red[500], p: 1, color: 'white' }}>Red 500 (main)</Box>
  <Box sx={{ bgcolor: red[900], p: 1, color: 'white' }}>Red 900 (darkest)</Box>
</Stack>
```

## Color Manipulation Functions

Utility functions for manipulating colors dynamically.

```typescript { .api }
/**
 * Adds alpha transparency to colors
 * @param color - Color string (hex, rgb, hsl, etc.)
 * @param value - Alpha value between 0 and 1
 * @returns Color string with alpha transparency
 */
function alpha(color: string, value: number): string;

/**
 * Darkens colors by mixing with black
 * @param color - Color string
 * @param coefficient - Darkening amount between 0 and 1
 * @returns Darkened color string
 */
function darken(color: string, coefficient: number): string;

/**
 * Lightens colors by mixing with white
 * @param color - Color string
 * @param coefficient - Lightening amount between 0 and 1
 * @returns Lightened color string
 */
function lighten(color: string, coefficient: number): string;

/**
 * Emphasizes colors (darkens light colors, lightens dark colors)
 * @param color - Color string
 * @param coefficient - Emphasis amount between 0 and 1
 * @returns Emphasized color string
 */
function emphasize(color: string, coefficient?: number): string;

/**
 * Calculates contrast ratio between two colors
 * @param foreground - Foreground color
 * @param background - Background color
 * @returns Contrast ratio (1-21, where 21 is maximum contrast)
 */
function getContrastRatio(foreground: string, background: string): number;

/**
 * Calculates relative luminance of a color
 * @param color - Color string
 * @returns Luminance value between 0 and 1
 */
function getLuminance(color: string): number;

/**
 * Converts hex color to RGB
 * @param hex - Hex color string (with or without #)
 * @returns RGB color string
 */
function hexToRgb(hex: string): string;

/**
 * Converts RGB color to hex
 * @param rgb - RGB color string
 * @returns Hex color string
 */
function rgbToHex(rgb: string): string;

/**
 * Converts HSL color to RGB
 * @param hsl - HSL color string
 * @returns RGB color string
 */
function hslToRgb(hsl: string): string;

/**
 * Decomposes color into its components
 * @param color - Color string
 * @returns Color object with type and values
 */
function decomposeColor(color: string): {
  type: string;
  values: number[];
  colorSpace?: string;
};

/**
 * Recomposes color from components
 * @param color - Color object
 * @returns Color string
 */
function recomposeColor(color: {
  type: string;
  values: number[];
  colorSpace?: string;
}): string;
```

**Usage Examples:**

```typescript
import { 
  alpha, 
  darken, 
  lighten, 
  emphasize, 
  getContrastRatio,
  getLuminance 
} from "@mui/material/styles";
import { blue } from "@mui/material/colors";

// Color manipulation in styled components
const StyledButton = styled(Button)(({ theme }) => ({
  backgroundColor: theme.palette.primary.main,
  '&:hover': {
    backgroundColor: darken(theme.palette.primary.main, 0.1),
  },
  '&:active': {
    backgroundColor: darken(theme.palette.primary.main, 0.2),
  },
  boxShadow: `0 2px 8px ${alpha(theme.palette.primary.main, 0.3)}`,
}));

// Using in sx prop
<Box
  sx={{
    bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
    border: (theme) => `1px solid ${lighten(theme.palette.primary.main, 0.5)}`,
    '&:hover': {
      bgcolor: (theme) => alpha(theme.palette.primary.main, 0.2),
    },
  }}
>
  Dynamically styled content
</Box>

// Contrast checking for accessibility
const textColor = getContrastRatio('#ffffff', blue[500]) > 4.5 ? '#ffffff' : '#000000';

// Luminance-based decisions
const backgroundColor = blue[500];
const textColor = getLuminance(backgroundColor) > 0.5 ? '#000000' : '#ffffff';
```

## Theme Color Configuration

```typescript { .api }
/**
 * Palette configuration interface
 */
interface PaletteOptions {
  mode?: 'light' | 'dark';
  primary?: PaletteColorOptions;
  secondary?: PaletteColorOptions;
  error?: PaletteColorOptions;
  warning?: PaletteColorOptions;
  info?: PaletteColorOptions;
  success?: PaletteColorOptions;
  grey?: Partial<ColorPalette>;
  common?: Partial<CommonColors>;
  text?: Partial<TypeText>;
  background?: Partial<TypeBackground>;
  action?: Partial<TypeAction>;
  divider?: string;
}

interface PaletteColorOptions {
  main: string;
  light?: string;
  dark?: string;
  contrastText?: string;
}

interface TypeText {
  primary: string;
  secondary: string;
  disabled: string;
}

interface TypeBackground {
  default: string;
  paper: string;
}

interface TypeAction {
  active: string;
  hover: string;
  hoverOpacity: number;
  selected: string;
  selectedOpacity: number;
  disabled: string;
  disabledBackground: string;
  disabledOpacity: number;
  focus: string;
  focusOpacity: number;
  activatedOpacity: number;
}
```

**Usage Examples:**

```typescript
import { createTheme } from "@mui/material/styles";
import { red, blue, green, orange, grey } from "@mui/material/colors";

// Custom color theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: blue[600],
      light: blue[400],
      dark: blue[800],
      contrastText: '#ffffff',
    },
    secondary: {
      main: orange[500],
      light: orange[300],
      dark: orange[700],
      contrastText: '#ffffff',
    },
    error: {
      main: red[600],
    },
    warning: {
      main: orange[800],
    },
    info: {
      main: blue[500],
    },
    success: {
      main: green[600],
    },
    grey: grey,
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.6)',
      disabled: 'rgba(0, 0, 0, 0.38)',
    },
    background: {
      default: '#fafafa',
      paper: '#ffffff',
    },
    divider: 'rgba(0, 0, 0, 0.12)',
  },
});

// Dark theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: blue[400],
    },
    secondary: {
      main: orange[400],
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
    },
  },
});
```

## Color Usage Patterns

### Semantic Color System

```typescript
// Using semantic colors
<Alert severity="success">Success message</Alert>
<Alert severity="error">Error message</Alert>
<Alert severity="warning">Warning message</Alert>
<Alert severity="info">Info message</Alert>

// Corresponding theme colors
<Button color="primary">Primary Action</Button>
<Button color="secondary">Secondary Action</Button>
<Button color="error">Delete Action</Button>
<Button color="success">Confirm Action</Button>
```

### Accessibility-Conscious Color Usage

```typescript
import { getContrastRatio } from "@mui/material/styles";

function AccessibleColorPicker({ backgroundColor }: { backgroundColor: string }) {
  // Ensure sufficient contrast for text
  const textColor = getContrastRatio('#ffffff', backgroundColor) >= 4.5 
    ? '#ffffff' 
    : '#000000';
  
  return (
    <Box
      sx={{
        bgcolor: backgroundColor,
        color: textColor,
        p: 2,
        borderRadius: 1,
      }}
    >
      This text maintains WCAG AA contrast requirements
    </Box>
  );
}
```

### Dynamic Color Theming

```typescript
function DynamicThemedComponent() {
  const theme = useTheme();
  
  return (
    <Box
      sx={{
        // Base color from theme
        bgcolor: 'primary.main',
        // Manipulated variants
        borderTop: `4px solid ${darken(theme.palette.primary.main, 0.2)}`,
        borderBottom: `4px solid ${lighten(theme.palette.primary.main, 0.2)}`,
        // Semi-transparent overlay
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: alpha(theme.palette.common.white, 0.1),
          pointerEvents: 'none',
        },
        // Hover state with emphasis
        '&:hover': {
          bgcolor: emphasize(theme.palette.primary.main, 0.1),
        },
      }}
    >
      Dynamically themed content
    </Box>
  );
}
```