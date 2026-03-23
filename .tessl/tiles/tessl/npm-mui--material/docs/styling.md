# Styling System

Comprehensive theming and styling system with theme creation, color manipulation, and CSS utilities.

## Capabilities

### Theme Creation

```typescript { .api }
/**
 * Creates custom themes
 * @param options - Theme configuration options
 * @returns Theme object
 */
function createTheme(options?: ThemeOptions): Theme;

/**
 * Extends themes with CSS variables support
 * @param options - Extended theme options
 * @returns Extended theme object
 */
function extendTheme(options?: CssVarsThemeOptions): Theme;

interface ThemeOptions {
  palette?: PaletteOptions;
  typography?: TypographyOptions;
  spacing?: SpacingOptions;
  breakpoints?: BreakpointsOptions;
  zIndex?: ZIndexOptions;
  transitions?: TransitionsOptions;
  components?: ComponentsOptions;
  mixins?: MixinsOptions;
  shadows?: Shadows;
  shape?: ShapeOptions;
}

interface Theme {
  palette: Palette;
  typography: Typography;
  spacing: Spacing;
  breakpoints: Breakpoints;
  zIndex: ZIndex;
  transitions: Transitions;
  components?: Components;
  mixins: Mixins;
  shadows: Shadows;
  shape: Shape;
}
```

### Theme Provider

```typescript { .api }
/**
 * Context provider for themes
 * @param props - ThemeProvider configuration
 * @returns ThemeProvider component
 */
function ThemeProvider(props: ThemeProviderProps): JSX.Element;

interface ThemeProviderProps {
  theme: Theme;
  children: React.ReactNode;
}
```

### Theme Hooks

```typescript { .api }
/**
 * Hook for accessing current theme
 * @returns Current theme object
 */
function useTheme(): Theme;

/**
 * Hook for merging component props with theme defaults
 * @param props - Component props and theme key
 * @returns Merged props with theme defaults
 */
function useThemeProps<T>(props: UseThemePropsProps<T>): T;

interface UseThemePropsProps<T> {
  props: T;
  name: string;
}
```

**Usage Examples:**

```typescript
import { createTheme, ThemeProvider, useTheme } from "@mui/material/styles";

// Custom theme creation
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#fff',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.125rem',
      fontWeight: 300,
    },
  },
  spacing: 8,
  shape: {
    borderRadius: 12,
  },
});

// Using theme provider
<ThemeProvider theme={theme}>
  <App />
</ThemeProvider>

// Using theme in components
function MyComponent() {
  const theme = useTheme();
  
  return (
    <Box
      sx={{
        color: theme.palette.primary.main,
        padding: theme.spacing(2),
        borderRadius: theme.shape.borderRadius,
      }}
    >
      Themed component
    </Box>
  );
}
```

### Styled Components

```typescript { .api }
/**
 * Styled-components API for creating styled components
 * @param component - Component to style
 * @returns Styled component factory
 */
function styled<C extends React.ComponentType<any>>(
  component: C
): StyledComponent<C>;

type StyledComponent<C> = (
  template: TemplateStringsArray | CSSObject | ((props: any) => CSSObject),
  ...args: any[]
) => React.ComponentType<React.ComponentProps<C>>;
```

**Usage Examples:**

```typescript
import { styled } from "@mui/material/styles";
import { Button, Box } from "@mui/material";

// Styled component with template literal
const StyledButton = styled(Button)(({ theme }) => ({
  color: theme.palette.primary.main,
  backgroundColor: theme.palette.primary.light,
  '&:hover': {
    backgroundColor: theme.palette.primary.main,
  },
}));

// Styled component with object syntax
const CustomBox = styled(Box)<{ highlighted?: boolean }>(({ theme, highlighted }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: highlighted ? theme.palette.action.selected : 'transparent',
}));

// Usage
<StyledButton variant="contained">Custom Button</StyledButton>
<CustomBox highlighted>Highlighted Box</CustomBox>
```

### Color Functions

```typescript { .api }
/**
 * Adds alpha transparency to colors
 * @param color - Color string
 * @param value - Alpha value (0-1)
 * @returns Color string with alpha
 */
function alpha(color: string, value: number): string;

/**
 * Darkens colors
 * @param color - Color string
 * @param coefficient - Darkening coefficient (0-1)
 * @returns Darkened color string
 */
function darken(color: string, coefficient: number): string;

/**
 * Lightens colors
 * @param color - Color string
 * @param coefficient - Lightening coefficient (0-1)
 * @returns Lightened color string
 */
function lighten(color: string, coefficient: number): string;

/**
 * Emphasizes colors (darkens light colors, lightens dark colors)
 * @param color - Color string
 * @param coefficient - Emphasis coefficient (0-1)
 * @returns Emphasized color string
 */
function emphasize(color: string, coefficient: number): string;

/**
 * Calculates contrast ratio between two colors
 * @param foreground - Foreground color
 * @param background - Background color
 * @returns Contrast ratio number
 */
function getContrastRatio(foreground: string, background: string): number;

/**
 * Calculates color luminance
 * @param color - Color string
 * @returns Luminance value (0-1)
 */
function getLuminance(color: string): number;
```

**Usage Examples:**

```typescript
import { alpha, darken, lighten, emphasize } from "@mui/material/styles";

// Using color functions in styled components
const StyledComponent = styled('div')(({ theme }) => ({
  backgroundColor: alpha(theme.palette.primary.main, 0.1),
  borderColor: darken(theme.palette.primary.main, 0.2),
  '&:hover': {
    backgroundColor: emphasize(theme.palette.primary.main, 0.15),
  },
}));

// Using in sx prop
<Box
  sx={{
    bgcolor: (theme) => alpha(theme.palette.error.main, 0.1),
    border: (theme) => `1px solid ${darken(theme.palette.error.main, 0.5)}`,
  }}
>
  Alert content
</Box>
```

### SX Prop System

```typescript { .api }
/**
 * SX prop type for inline styling with theme integration
 */
type SxProps<Theme = {}> = 
  | SystemStyleObject<Theme>
  | ((theme: Theme) => SystemStyleObject<Theme>)
  | Array<SystemStyleObject<Theme> | ((theme: Theme) => SystemStyleObject<Theme>)>;

interface SystemStyleObject<Theme = {}> {
  // Spacing
  m?: number | string;
  mt?: number | string;
  mr?: number | string;
  mb?: number | string;
  ml?: number | string;
  mx?: number | string;
  my?: number | string;
  p?: number | string;
  pt?: number | string;
  pr?: number | string;
  pb?: number | string;
  pl?: number | string;
  px?: number | string;
  py?: number | string;
  
  // Colors
  color?: string;
  bgcolor?: string;
  backgroundColor?: string;
  
  // Typography
  fontFamily?: string;
  fontSize?: number | string;
  fontWeight?: number | string;
  fontStyle?: string;
  textAlign?: string;
  
  // Layout
  display?: string;
  position?: string;
  top?: number | string;
  right?: number | string;
  bottom?: number | string;
  left?: number | string;
  width?: number | string;
  height?: number | string;
  minWidth?: number | string;
  minHeight?: number | string;
  maxWidth?: number | string;
  maxHeight?: number | string;
  
  // Flexbox
  flexDirection?: string;
  flexWrap?: string;
  justifyContent?: string;
  alignItems?: string;
  alignContent?: string;
  alignSelf?: string;
  flex?: number | string;
  flexGrow?: number;
  flexShrink?: number;
  flexBasis?: number | string;
  
  // Borders
  border?: number | string;
  borderTop?: number | string;
  borderRight?: number | string;
  borderBottom?: number | string;
  borderLeft?: number | string;
  borderColor?: string;
  borderRadius?: number | string;
  
  // Other properties
  opacity?: number;
  overflow?: string;
  textOverflow?: string;
  whiteSpace?: string;
  
  // Responsive breakpoints
  [key: string]: any;
}
```

**Usage Examples:**

```typescript
import { Box, Typography } from "@mui/material";

// Basic sx usage
<Box
  sx={{
    p: 2,
    m: 1,
    bgcolor: 'primary.main',
    color: 'white',
    borderRadius: 1,
  }}
>
  Styled with sx
</Box>

// Responsive sx
<Typography
  sx={{
    fontSize: {
      xs: '1rem',
      sm: '1.25rem',
      md: '1.5rem',
    },
    textAlign: {
      xs: 'center',
      md: 'left',
    },
  }}
>
  Responsive text
</Typography>

// Function-based sx with theme
<Box
  sx={(theme) => ({
    p: theme.spacing(2),
    bgcolor: alpha(theme.palette.primary.main, 0.1),
    border: `1px solid ${theme.palette.primary.main}`,
    borderRadius: theme.shape.borderRadius,
    '&:hover': {
      bgcolor: alpha(theme.palette.primary.main, 0.2),
    },
  })}
>
  Theme-aware styling
</Box>
```

### Responsive Breakpoints

```typescript { .api }
/**
 * Default breakpoint values and utilities
 */
interface Breakpoints {
  keys: BreakpointKey[];
  values: BreakpointValues;
  up: (key: BreakpointKey) => string;
  down: (key: BreakpointKey) => string;
  between: (start: BreakpointKey, end: BreakpointKey) => string;
  only: (key: BreakpointKey) => string;
}

type BreakpointKey = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

interface BreakpointValues {
  xs: number; // 0
  sm: number; // 600
  md: number; // 900
  lg: number; // 1200
  xl: number; // 1536
}

/**
 * Hook for responsive design with media queries
 * @param query - Media query string or function
 * @returns Boolean indicating if query matches
 */
function useMediaQuery<Theme = DefaultTheme>(
  query: string | ((theme: Theme) => string),
  options?: UseMediaQueryOptions
): boolean;
```

**Usage Examples:**

```typescript
import { useMediaQuery, useTheme } from "@mui/material";

function ResponsiveComponent() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isLarge = useMediaQuery(theme.breakpoints.up('lg'));
  
  return (
    <Box
      sx={{
        p: isMobile ? 1 : 3,
        display: {
          xs: 'block',
          md: 'flex',
        },
        flexDirection: {
          md: 'row',
          lg: 'column',
        },
      }}
    >
      <Typography variant={isMobile ? 'h6' : 'h4'}>
        {isLarge ? 'Large Screen' : 'Regular Screen'}
      </Typography>
    </Box>
  );
}
```

### CSS Utilities

```typescript { .api }
/**
 * CSS-in-JS function
 */
function css(template: TemplateStringsArray, ...args: any[]): SerializedStyles;

/**
 * Keyframes for animations
 */
function keyframes(template: TemplateStringsArray, ...args: any[]): Keyframes;

/**
 * Global styles component
 * @param props - GlobalStyles configuration
 * @returns GlobalStyles component
 */
function GlobalStyles(props: GlobalStylesProps): JSX.Element;

interface GlobalStylesProps {
  styles: CSSObject | string | ((theme: Theme) => CSSObject | string);
}
```

**Usage Examples:**

```typescript
import { GlobalStyles, keyframes } from "@mui/material";

// Keyframe animation
const fadeIn = keyframes`
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
`;

// Global styles
<GlobalStyles
  styles={{
    '*': {
      boxSizing: 'border-box',
    },
    html: {
      fontSize: '16px',
    },
    body: {
      margin: 0,
      fontFamily: '"Roboto", sans-serif',
    },
  }}
/>

// Theme-aware global styles
<GlobalStyles
  styles={(theme) => ({
    '.custom-class': {
      color: theme.palette.primary.main,
      padding: theme.spacing(2),
    },
  })}
/>
```