# Utility Components

Utility components for common functionality including click-away listeners, portals, transitions, and hooks.

## Capabilities

### ClickAwayListener

Utility component for detecting clicks outside an element.

```typescript { .api }
/**
 * Utility component for detecting clicks outside element
 * @param props - ClickAwayListener configuration
 * @returns ClickAwayListener component
 */
function ClickAwayListener(props: ClickAwayListenerProps): JSX.Element;

interface ClickAwayListenerProps {
  /** The wrapped element */
  children: React.ReactElement;
  /** If true, the React tree is ignored and only the DOM tree is considered */
  disableReactTree?: boolean;
  /** The mouse event to listen to */
  mouseEvent?: 'onClick' | 'onMouseDown' | 'onMouseUp' | false;
  /** Callback fired when a "click away" event is detected */
  onClickAway: (event: MouseEvent | TouchEvent) => void;
  /** The touch event to listen to */
  touchEvent?: 'onTouchStart' | 'onTouchEnd' | false;
}
```

### Portal

Component for rendering children into a DOM node outside the normal hierarchy.

```typescript { .api }
/**
 * Component for rendering children outside normal hierarchy
 * @param props - Portal configuration
 * @returns Portal component
 */
function Portal(props: PortalProps): JSX.Element;

interface PortalProps {
  /** The children to render into the container */
  children?: React.ReactNode;
  /** An HTML element or a function that returns one */
  container?: Element | (() => Element | null) | null;
  /** If true, the children stay within their DOM hierarchy */
  disablePortal?: boolean;
}
```

### Transitions

Transition components for animating component state changes.

```typescript { .api }
/**
 * Fade transition component
 * @param props - Fade configuration
 * @returns Fade component
 */
function Fade(props: FadeProps): JSX.Element;

/**
 * Grow transition component
 * @param props - Grow configuration
 * @returns Grow component
 */
function Grow(props: GrowProps): JSX.Element;

/**
 * Slide transition component
 * @param props - Slide configuration
 * @returns Slide component
 */
function Slide(props: SlideProps): JSX.Element;

/**
 * Collapse transition component
 * @param props - Collapse configuration
 * @returns Collapse component
 */
function Collapse(props: CollapseProps): JSX.Element;

/**
 * Zoom transition component
 * @param props - Zoom configuration
 * @returns Zoom component
 */
function Zoom(props: ZoomProps): JSX.Element;

interface FadeProps extends TransitionProps {
  /** A single child content element */
  children?: React.ReactElement;
  /** The transition timing function */
  easing?: {
    enter?: string;
    exit?: string;
  } | string;
  /** If true, the component will transition in */
  in?: boolean;
  /** The duration for the transition */
  timeout?: number | {
    appear?: number;
    enter?: number;
    exit?: number;
  };
}

interface GrowProps extends TransitionProps {
  /** A single child content element */
  children?: React.ReactElement;
  /** If true, the component will transition in */
  in?: boolean;
  /** The duration for the transition */
  timeout?: number | 'auto' | {
    appear?: number;
    enter?: number;
    exit?: number;
  };
}

interface SlideProps extends TransitionProps {
  /** A single child content element */
  children?: React.ReactElement;
  /** An HTML element, or a function that returns one */
  container?: Element | (() => Element | null) | null;
  /** Direction the child node will enter from */
  direction?: 'left' | 'right' | 'up' | 'down';
  /** If true, the component will transition in */
  in?: boolean;
  /** The duration for the transition */
  timeout?: number | {
    appear?: number;
    enter?: number;
    exit?: number;
  };
}

interface CollapseProps extends TransitionProps {
  /** The content node to be collapsed */
  children?: React.ReactNode;
  /** The width (horizontal) or height (vertical) of the container when collapsed */
  collapsedSize?: number | string;
  /** The component used for the root node */
  component?: React.ElementType;
  /** If true, the component will transition in */
  in?: boolean;
  /** The collapse transition orientation */
  orientation?: 'horizontal' | 'vertical';
  /** The duration for the transition */
  timeout?: number | 'auto' | {
    appear?: number;
    enter?: number;
    exit?: number;
  };
}

interface ZoomProps extends TransitionProps {
  /** A single child content element */
  children?: React.ReactElement;
  /** If true, the component will transition in */
  in?: boolean;
  /** The duration for the transition */
  timeout?: number | {
    appear?: number;
    enter?: number;
    exit?: number;
  };
}
```

**Usage Examples:**

```typescript
import { 
  ClickAwayListener,
  Portal,
  Fade,
  Grow,
  Slide,
  Collapse,
  Zoom,
  Box,
  Button,
  Paper
} from "@mui/material";

// ClickAwayListener example
function DropdownMenu() {
  const [open, setOpen] = useState(false);

  const handleClickAway = () => {
    setOpen(false);
  };

  return (
    <ClickAwayListener onClickAway={handleClickAway}>
      <Box>
        <Button onClick={() => setOpen(!open)}>
          Toggle Menu
        </Button>
        {open && (
          <Paper sx={{ position: 'absolute', mt: 1, p: 1 }}>
            Menu content
          </Paper>
        )}
      </Box>
    </ClickAwayListener>
  );
}

// Portal example
<Portal container={document.body}>
  <Box sx={{ position: 'fixed', top: 0, left: 0, zIndex: 9999 }}>
    This content is rendered in document.body
  </Box>
</Portal>

// Transition examples
<Fade in={fadeIn} timeout={500}>
  <Box>Fade transition content</Box>
</Fade>

<Grow in={growIn} timeout={300}>
  <Paper elevation={4} sx={{ p: 2 }}>
    Grow transition content
  </Paper>
</Grow>

<Slide direction="up" in={slideIn} mountOnEnter unmountOnExit>
  <Alert severity="success">
    Slide transition alert
  </Alert>
</Slide>

<Collapse in={collapseIn}>
  <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
    Collapsible content that can be hidden or shown
  </Box>
</Collapse>
```

### Hooks

Utility hooks for common functionality.

```typescript { .api }
/**
 * Hook for responsive design with media queries
 * @param query - Media query string or function
 * @param options - Additional options
 * @returns Boolean indicating if query matches
 */
function useMediaQuery<Theme = DefaultTheme>(
  query: string | ((theme: Theme) => string),
  options?: UseMediaQueryOptions
): boolean;

/**
 * Hook for triggering actions based on scroll position
 * @param options - Scroll trigger options
 * @returns Boolean indicating if trigger is active
 */
function useScrollTrigger(options?: UseScrollTriggerOptions): boolean;

interface UseMediaQueryOptions {
  /** The default value for the match result */
  defaultMatches?: boolean;
  /** Whether to match during hydration */
  matchMedia?: (query: string) => { matches: boolean; media: string; onchange: any; addListener: any; removeListener: any; };
  /** If true, the hook will not re-render on media query changes */
  noSsr?: boolean;
  /** If true, SSR compatibility mode is enabled */
  ssrMatchMedia?: (query: string) => { matches: boolean };
}

interface UseScrollTriggerOptions {
  /** The node to listen to for scroll events */
  target?: Node | Window;
  /** If true, hide trigger will be true when scrolling down */
  disableHysteresis?: boolean;
  /** The scroll threshold */
  threshold?: number;
}
```

**Usage Examples:**

```typescript
import { useMediaQuery, useScrollTrigger, useTheme } from "@mui/material";
import { AppBar, Toolbar, Typography, Slide } from "@mui/material";

// Media query hook
function ResponsiveComponent() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.between('md', 'lg'));
  const isDesktop = useMediaQuery(theme.breakpoints.up('lg'));

  return (
    <Box>
      {isMobile && <Typography>Mobile View</Typography>}
      {isTablet && <Typography>Tablet View</Typography>}
      {isDesktop && <Typography>Desktop View</Typography>}
    </Box>
  );
}

// Scroll trigger hook
function HideOnScroll({ children }: { children: React.ReactElement }) {
  const trigger = useScrollTrigger({
    target: window,
    disableHysteresis: true,
    threshold: 100,
  });

  return (
    <Slide appear={false} direction="down" in={!trigger}>
      {children}
    </Slide>
  );
}

// Usage with AppBar
<HideOnScroll>
  <AppBar>
    <Toolbar>
      <Typography variant="h6">Hide on Scroll AppBar</Typography>
    </Toolbar>
  </AppBar>
</HideOnScroll>
```

### NoSsr

Utility component for preventing server-side rendering.

```typescript { .api }
/**
 * Utility component for preventing server-side rendering
 * @param props - NoSsr configuration
 * @returns NoSsr component
 */
function NoSsr(props: NoSsrProps): JSX.Element;

interface NoSsrProps {
  /** The content */
  children?: React.ReactNode;
  /** If true, the component will defer the rendering of the children into a different screen frame */
  defer?: boolean;
  /** The fallback content to display during SSR */
  fallback?: React.ReactNode;
}
```

### TextareaAutosize

Auto-resizing textarea component.

```typescript { .api }
/**
 * Auto-resizing textarea component
 * @param props - TextareaAutosize configuration
 * @returns TextareaAutosize component
 */
function TextareaAutosize(props: TextareaAutosizeProps): JSX.Element;

interface TextareaAutosizeProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  /** Maximum number of rows to display */
  maxRows?: number;
  /** Minimum number of rows to display */
  minRows?: number;
  /** Callback fired when the textarea is resized */
  onResize?: (event: Event) => void;
}
```

**Usage Examples:**

```typescript
import { NoSsr, TextareaAutosize, Box } from "@mui/material";

// NoSsr example - useful for components that behave differently on client vs server
<NoSsr fallback={<Box>Loading...</Box>}>
  <SomeClientOnlyComponent />
</NoSsr>

// TextareaAutosize example
<TextareaAutosize
  minRows={3}
  maxRows={10}
  placeholder="Enter your message here..."
  style={{
    width: '100%',
    fontSize: '16px',
    fontFamily: 'inherit',
    padding: '8px',
    border: '1px solid #ccc',
    borderRadius: '4px',
    resize: 'none',
  }}
/>
```

## Common Utility Patterns

### Conditional Rendering with Media Queries

```typescript
import { useMediaQuery, useTheme, Hidden } from "@mui/material";

function ConditionalContent() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <Box>
      {/* Using hook */}
      {isMobile ? (
        <MobileNavigation />
      ) : (
        <DesktopNavigation />
      )}
      
      {/* Using Hidden component (deprecated but still available) */}
      <Hidden mdDown>
        <DesktopSidebar />
      </Hidden>
      <Hidden mdUp>
        <MobileDrawer />
      </Hidden>
    </Box>
  );
}
```

### Scroll-based Interactions

```typescript
import { useScrollTrigger, Fab, Zoom } from "@mui/material";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";

function ScrollToTop() {
  const trigger = useScrollTrigger({
    disableHysteresis: true,
    threshold: 100,
  });

  const handleClick = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  return (
    <Zoom in={trigger}>
      <Fab
        onClick={handleClick}
        color="primary"
        size="small"
        aria-label="scroll back to top"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
        }}
      >
        <KeyboardArrowUpIcon />
      </Fab>
    </Zoom>
  );
}
```