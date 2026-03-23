# Layout Components

Responsive layout and container components for structuring applications with Material Design spacing and breakpoints.

## Capabilities

### Container

Responsive container component for centering and constraining content within defined max-widths.

```typescript { .api }
/**
 * Container component for centering and constraining content
 * @param props - Container configuration
 * @returns Container component
 */
function Container(props: ContainerProps): JSX.Element;

interface ContainerProps extends CommonProps {
  /** The max-width to apply to the container */
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false;
  /** If true, the left and right padding is removed */
  disableGutters?: boolean;
  /** Set the max-width to match the min-width of the current breakpoint */
  fixed?: boolean;
  /** The component used for the root node */
  component?: React.ElementType;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Container, Typography } from "@mui/material";

// Basic container
<Container maxWidth="lg">
  <Typography variant="h1">Centered Content</Typography>
</Container>

// Fluid container without gutters
<Container maxWidth={false} disableGutters>
  <Typography>Full width content</Typography>
</Container>
```

### Grid

Flexible grid layout component using CSS Flexbox with responsive breakpoints.

```typescript { .api }
/**
 * Grid layout component using CSS Flexbox
 * @param props - Grid configuration
 * @returns Grid component
 */
function Grid(props: GridProps): JSX.Element;

interface GridProps extends CommonProps {
  /** If true, defines a flex container */
  container?: boolean;
  /** If true, defines a flex item */
  item?: boolean;
  /** Defines spacing between children */
  spacing?: number | string;
  /** Number of columns to span on xs breakpoint */
  xs?: boolean | number | 'auto';
  /** Number of columns to span on sm breakpoint */
  sm?: boolean | number | 'auto';
  /** Number of columns to span on md breakpoint */
  md?: boolean | number | 'auto';
  /** Number of columns to span on lg breakpoint */
  lg?: boolean | number | 'auto';
  /** Number of columns to span on xl breakpoint */
  xl?: boolean | number | 'auto';
  /** Defines flex-direction style property */
  direction?: 'row' | 'row-reverse' | 'column' | 'column-reverse';
  /** Defines justify-content style property */
  justifyContent?: 'flex-start' | 'center' | 'flex-end' | 'space-between' | 'space-around' | 'space-evenly';
  /** Defines align-items style property */
  alignItems?: 'flex-start' | 'center' | 'flex-end' | 'stretch' | 'baseline';
  /** The component used for the root node */
  component?: React.ElementType;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Grid, Paper } from "@mui/material";

// Responsive grid layout
<Grid container spacing={3}>
  <Grid item xs={12} md={6}>
    <Paper>Item 1</Paper>
  </Grid>
  <Grid item xs={12} md={6}>
    <Paper>Item 2</Paper>
  </Grid>
</Grid>

// Custom alignment
<Grid container spacing={2} justifyContent="center" alignItems="center">
  <Grid item xs={6}>
    <Paper>Centered Item</Paper>
  </Grid>
</Grid>
```

### Stack

One-dimensional layout component for vertical or horizontal stacking with consistent spacing.

```typescript { .api }
/**
 * One-dimensional layout component for stacking
 * @param props - Stack configuration
 * @returns Stack component
 */
function Stack(props: StackProps): JSX.Element;

interface StackProps extends CommonProps {
  /** The direction to stack items */
  direction?: 'row' | 'row-reverse' | 'column' | 'column-reverse';
  /** Defines spacing between children */
  spacing?: number | string;
  /** Element placed between each child */
  divider?: React.ReactNode;
  /** Defines align-items style property */
  alignItems?: 'flex-start' | 'center' | 'flex-end' | 'stretch' | 'baseline';
  /** Defines justify-content style property */
  justifyContent?: 'flex-start' | 'center' | 'flex-end' | 'space-between' | 'space-around' | 'space-evenly';
  /** The component used for the root node */
  component?: React.ElementType;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Stack, Button, Divider } from "@mui/material";

// Vertical stack with spacing
<Stack spacing={2}>
  <Button variant="contained">Button 1</Button>
  <Button variant="contained">Button 2</Button>
  <Button variant="contained">Button 3</Button>
</Stack>

// Horizontal stack with divider
<Stack direction="row" spacing={1} divider={<Divider orientation="vertical" flexItem />}>
  <Button>Home</Button>
  <Button>About</Button>
  <Button>Contact</Button>
</Stack>
```

### Box

Most basic layout component providing a wrapper with access to system styling props.

```typescript { .api }
/**
 * Basic layout component with system props
 * @param props - Box configuration
 * @returns Box component
 */
function Box(props: BoxProps): JSX.Element;

interface BoxProps extends CommonProps {
  /** The component used for the root node */
  component?: React.ElementType;
  /** All system props (spacing, colors, typography, etc.) */
  m?: number | string; // margin
  p?: number | string; // padding
  mt?: number | string; // margin-top
  mb?: number | string; // margin-bottom
  ml?: number | string; // margin-left
  mr?: number | string; // margin-right
  pt?: number | string; // padding-top
  pb?: number | string; // padding-bottom
  pl?: number | string; // padding-left
  pr?: number | string; // padding-right
  color?: string;
  bgcolor?: string;
  border?: number | string;
  borderRadius?: number | string;
  display?: string;
  flexDirection?: string;
  alignItems?: string;
  justifyContent?: string;
  width?: number | string;
  height?: number | string;
  minWidth?: number | string;
  minHeight?: number | string;
  maxWidth?: number | string;
  maxHeight?: number | string;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Box, Typography } from "@mui/material";

// Box with spacing and colors
<Box p={3} bgcolor="primary.main" color="white" borderRadius={2}>
  <Typography>Styled Box</Typography>
</Box>

// Box as flex container
<Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
  <Typography variant="h4">Centered Content</Typography>
</Box>

// Responsive Box with breakpoint-specific props
<Box
  width={{
    xs: '100%',
    sm: '50%',
    md: '25%'
  }}
  p={{
    xs: 1,
    sm: 2,
    md: 3
  }}
>
  <Typography>Responsive Box</Typography>
</Box>
```

## Common Layout Patterns

### Page Layout

```typescript
import { Container, Box, AppBar, Toolbar, Typography } from "@mui/material";

function PageLayout({ children }: { children: React.ReactNode }) {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">My App</Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {children}
      </Container>
    </Box>
  );
}
```

### Sidebar Layout

```typescript
import { Box, Drawer, AppBar, Toolbar, Typography } from "@mui/material";

const drawerWidth = 240;

function SidebarLayout({ children }: { children: React.ReactNode }) {
  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6">App Title</Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar />
        {/* Sidebar content */}
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}
```

## Responsive Breakpoints

```typescript { .api }
// Default breakpoint values
interface Breakpoints {
  values: {
    xs: 0;
    sm: 600;
    md: 900;
    lg: 1200;
    xl: 1536;
  };
}

// Breakpoint helpers
function useMediaQuery(query: string): boolean;
```

**Usage Examples:**

```typescript
import { useMediaQuery, useTheme } from "@mui/material";

function ResponsiveComponent() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  return (
    <Box p={isMobile ? 1 : 3}>
      <Typography variant={isMobile ? "h6" : "h4"}>
        Responsive Typography
      </Typography>
    </Box>
  );
}
```