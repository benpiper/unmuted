# Feedback Components

User feedback components including alerts, progress indicators, dialogs, and snackbars.

## Capabilities

### Alert

Alert component for displaying important messages with different severity levels.

```typescript { .api }
/**
 * Alert component for important messages
 * @param props - Alert configuration
 * @returns Alert component
 */
function Alert(props: AlertProps): JSX.Element;

interface AlertProps extends CommonProps {
  /** The action to display */
  action?: React.ReactNode;
  /** Override the default label for the close popup icon button */
  closeText?: string;
  /** The main color of the Alert */
  color?: 'error' | 'info' | 'success' | 'warning';
  /** Override the icon displayed before the children */
  icon?: React.ReactNode;
  /** The component maps the severity prop to a range of different icons */
  iconMapping?: Partial<{
    error: React.ReactNode;
    info: React.ReactNode;
    success: React.ReactNode;
    warning: React.ReactNode;
  }>;
  /** Callback fired when the component requests to be closed */
  onClose?: (event: React.SyntheticEvent) => void;
  /** The ARIA role attribute of the element */
  role?: string;
  /** The severity of the alert */
  severity?: 'error' | 'info' | 'success' | 'warning';
  /** The variant to use */
  variant?: 'filled' | 'outlined' | 'standard';
  children?: React.ReactNode;
}
```

### Progress Indicators

Circular and linear progress indicators for loading states.

```typescript { .api }
/**
 * Circular progress indicator
 * @param props - CircularProgress configuration
 * @returns CircularProgress component
 */
function CircularProgress(props: CircularProgressProps): JSX.Element;

/**
 * Linear progress indicator
 * @param props - LinearProgress configuration
 * @returns LinearProgress component
 */
function LinearProgress(props: LinearProgressProps): JSX.Element;

interface CircularProgressProps extends CommonProps {
  /** The color of the component */
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' | 'inherit';
  /** If true, the shrink animation is disabled */
  disableShrink?: boolean;
  /** The size of the component */
  size?: number | string;
  /** The thickness of the circle */
  thickness?: number;
  /** The value of the progress indicator for the determinate variant */
  value?: number;
  /** The variant to use */
  variant?: 'determinate' | 'indeterminate';
}

interface LinearProgressProps extends CommonProps {
  /** The color of the component */
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' | 'inherit';
  /** The value of the progress indicator for the determinate and buffer variants */
  value?: number;
  /** The value for the buffer variant */
  valueBuffer?: number;
  /** The variant to use */
  variant?: 'determinate' | 'indeterminate' | 'buffer' | 'query';
}
```

### Dialog

Dialog component for modal content and user interaction.

```typescript { .api }
/**
 * Dialog component for modal content
 * @param props - Dialog configuration
 * @returns Dialog component
 */
function Dialog(props: DialogProps): JSX.Element;

/**
 * Title section of dialog
 * @param props - DialogTitle configuration
 * @returns DialogTitle component
 */
function DialogTitle(props: DialogTitleProps): JSX.Element;

/**
 * Main dialog content area
 * @param props - DialogContent configuration
 * @returns DialogContent component
 */
function DialogContent(props: DialogContentProps): JSX.Element;

/**
 * Container for dialog actions
 * @param props - DialogActions configuration
 * @returns DialogActions component
 */
function DialogActions(props: DialogActionsProps): JSX.Element;

interface DialogProps extends CommonProps {
  /** The id(s) of the element(s) that describe the dialog */
  'aria-describedby'?: string;
  /** The id(s) of the element(s) that label the dialog */
  'aria-labelledby'?: string;
  /** If true, the dialog is full-screen */
  fullScreen?: boolean;
  /** If true, the dialog stretches to maxWidth */
  fullWidth?: boolean;
  /** Determine the max-width of the dialog */
  maxWidth?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | false;
  /** Callback fired when the component requests to be closed */
  onClose?: (event: {}, reason: 'escapeKeyDown' | 'backdropClick') => void;
  /** If true, the component is shown */
  open: boolean;
  /** The component used to render the body of the dialog */
  PaperComponent?: React.ComponentType<PaperProps>;
  /** Props applied to the Paper element */
  PaperProps?: Partial<PaperProps>;
  /** Determine the container for scrolling the dialog */
  scroll?: 'body' | 'paper';
  /** The component used for the transition */
  TransitionComponent?: React.ComponentType<TransitionProps>;
  /** The duration for the transition */
  transitionDuration?: TransitionProps['timeout'];
  /** Props applied to the transition element */
  TransitionProps?: TransitionProps;
  children?: React.ReactNode;
}

interface DialogTitleProps extends CommonProps {
  children?: React.ReactNode;
}

interface DialogContentProps extends CommonProps {
  /** Display the top and bottom dividers */
  dividers?: boolean;
  children?: React.ReactNode;
}

interface DialogActionsProps extends CommonProps {
  /** If true, the actions do not have additional margin */
  disableSpacing?: boolean;
  children?: React.ReactNode;
}
```

### Snackbar

Brief message component displayed at the bottom of the screen.

```typescript { .api }
/**
 * Brief message component at bottom of screen
 * @param props - Snackbar configuration
 * @returns Snackbar component
 */
function Snackbar(props: SnackbarProps): JSX.Element;

interface SnackbarProps extends CommonProps {
  /** The action to display */
  action?: React.ReactNode;
  /** The anchor of the Snackbar */
  anchorOrigin?: {
    vertical: 'top' | 'bottom';
    horizontal: 'left' | 'center' | 'right';
  };
  /** The number of milliseconds to wait before automatically calling onClose */
  autoHideDuration?: number | null;
  /** Props applied to the ClickAwayListener element */
  ClickAwayListenerProps?: Partial<ClickAwayListenerProps>;
  /** Props applied to the SnackbarContent element */
  ContentProps?: Partial<SnackbarContentProps>;
  /** If true, the autoHideDuration timer will expire even if the window is not focused */
  disableWindowBlurListener?: boolean;
  /** When displaying multiple consecutive Snackbars from a parent rendering a single <Snackbar/> */
  key?: any;
  /** The message to display */
  message?: React.ReactNode;
  /** Callback fired when the component requests to be closed */
  onClose?: (event: React.SyntheticEvent | Event, reason: string) => void;
  /** If true, the component is shown */
  open?: boolean;
  /** The number of milliseconds to wait before dismissing after user interaction */
  resumeHideDuration?: number;
  /** The component used for the transition */
  TransitionComponent?: React.ComponentType<TransitionProps>;
  /** The duration for the transition */
  transitionDuration?: TransitionProps['timeout'];
  /** Props applied to the transition element */
  TransitionProps?: TransitionProps;
}
```

**Usage Examples:**

```typescript
import { 
  Alert, 
  AlertTitle,
  CircularProgress, 
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Button,
  Box
} from "@mui/material";

// Alert examples
<Alert severity="success">
  <AlertTitle>Success</AlertTitle>
  This is a success alert — check it out!
</Alert>

<Alert severity="error" onClose={() => setShowAlert(false)}>
  This is an error alert with close action.
</Alert>

// Progress indicators
<Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
  <CircularProgress />
  <CircularProgress color="secondary" />
  <CircularProgress variant="determinate" value={75} />
</Box>

<Box sx={{ width: '100%' }}>
  <LinearProgress />
  <LinearProgress variant="determinate" value={50} />
</Box>

// Dialog example
<Dialog open={dialogOpen} onClose={handleClose} maxWidth="sm" fullWidth>
  <DialogTitle>Confirm Action</DialogTitle>
  <DialogContent>
    Are you sure you want to delete this item? This action cannot be undone.
  </DialogContent>
  <DialogActions>
    <Button onClick={handleClose}>Cancel</Button>
    <Button onClick={handleConfirm} variant="contained" color="error">
      Delete
    </Button>
  </DialogActions>
</Dialog>

// Snackbar example
<Snackbar
  open={snackbarOpen}
  autoHideDuration={6000}
  onClose={handleSnackbarClose}
  message="Item successfully saved"
  action={
    <Button color="inherit" size="small" onClick={handleSnackbarClose}>
      Close
    </Button>
  }
/>
```

### Skeleton

Skeleton placeholder component for loading states.

```typescript { .api }
/**
 * Skeleton placeholder for loading states
 * @param props - Skeleton configuration
 * @returns Skeleton component
 */
function Skeleton(props: SkeletonProps): JSX.Element;

interface SkeletonProps extends CommonProps {
  /** The animation effect */
  animation?: 'pulse' | 'wave' | false;
  /** The component used for the root node */
  component?: React.ElementType;
  /** Height of the skeleton */
  height?: number | string;
  /** The type of content that will be rendered */
  variant?: 'text' | 'rectangular' | 'rounded' | 'circular';
  /** Width of the skeleton */
  width?: number | string;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Skeleton, Card, CardContent, Typography, Box } from "@mui/material";

// Loading card skeleton
<Card>
  <CardContent>
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
      <Skeleton variant="circular" width={40} height={40} />
      <Box sx={{ ml: 2, flex: 1 }}>
        <Skeleton variant="text" width="60%" />
        <Skeleton variant="text" width="40%" />
      </Box>
    </Box>
    <Skeleton variant="rectangular" height={200} />
    <Box sx={{ mt: 2 }}>
      <Skeleton variant="text" />
      <Skeleton variant="text" width="80%" />
    </Box>
  </CardContent>
</Card>

// Text loading skeleton
<Box>
  <Skeleton variant="text" sx={{ fontSize: '2rem' }} />
  <Skeleton variant="text" />
  <Skeleton variant="text" width="60%" />
</Box>
```

### Modal

Base modal component for overlaying content on the current page.

```typescript { .api }
/**
 * Base modal component for overlaying content on the current page
 * @param props - Modal configuration
 * @returns Modal component
 */
function Modal(props: ModalProps): JSX.Element;

interface ModalProps extends CommonProps {
  /** A single child content element */
  children: React.ReactElement;
  /** If true, the component is shown */
  open: boolean;
  /** Callback fired when the component requests to be closed */
  onClose?: (event: {}, reason: 'backdropClick' | 'escapeKeyDown') => void;
  /** If true, the modal will not automatically shift focus to itself */
  disableAutoFocus?: boolean;
  /** If true, the modal will not prevent focus from leaving the modal */
  disableEnforceFocus?: boolean;
  /** If true, hitting escape will not fire the onClose callback */
  disableEscapeKeyDown?: boolean;
  /** If true, the modal will not restore focus to previously focused element after closing */
  disableRestoreFocus?: boolean;
  /** If true, the backdrop will not shift the scrollbar */
  disableScrollLock?: boolean;
  /** If true, clicking the backdrop will not fire the onClose callback */
  hideBackdrop?: boolean;
  /** If true, the modal will restore focus to previously focused element on close */
  keepMounted?: boolean;
}
```

**Usage Examples:**

```typescript
import { Modal, Box, Typography, Button } from "@mui/material";

const [open, setOpen] = React.useState(false);

// Basic modal
<Modal
  open={open}
  onClose={() => setOpen(false)}
>
  <Box sx={{
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    border: '2px solid #000',
    boxShadow: 24,
    p: 4,
  }}>
    <Typography variant="h6">Modal Title</Typography>
    <Typography sx={{ mt: 2 }}>
      Modal content goes here
    </Typography>
    <Button onClick={() => setOpen(false)} sx={{ mt: 2 }}>
      Close
    </Button>
  </Box>
</Modal>
```

### Backdrop

Backdrop component for displaying overlay behind modal content.

```typescript { .api }
/**
 * Backdrop component for displaying overlay behind modal content
 * @param props - Backdrop configuration
 * @returns Backdrop component
 */
function Backdrop(props: BackdropProps): JSX.Element;

interface BackdropProps extends CommonProps {
  /** The content of the component */
  children?: React.ReactNode;
  /** If true, the backdrop is invisible */
  invisible?: boolean;
  /** If true, the backdrop is open */
  open: boolean;
  /** The component used for the transition */
  TransitionComponent?: React.ComponentType<any>;
  /** The duration for the transition */
  transitionDuration?: number | { appear?: number; enter?: number; exit?: number };
  /** Callback fired when clicked */
  onClick?: React.MouseEventHandler<HTMLDivElement>;
}
```

**Usage Examples:**

```typescript
import { Backdrop, CircularProgress, Button } from "@mui/material";

const [open, setOpen] = React.useState(false);

// Loading backdrop
<Backdrop
  sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
  open={open}
  onClick={() => setOpen(false)}
>
  <CircularProgress color="inherit" />
</Backdrop>

// Trigger button
<Button onClick={() => setOpen(true)}>
  Show Backdrop
</Button>
```

### AlertTitle

Title component for Alert messages.

```typescript { .api }
/**
 * Title component for Alert messages
 * @param props - AlertTitle configuration
 * @returns AlertTitle component
 */
function AlertTitle(props: AlertTitleProps): JSX.Element;

interface AlertTitleProps extends CommonProps {
  /** The content of the component */
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Alert, AlertTitle } from "@mui/material";

// Alert with title
<Alert severity="error">
  <AlertTitle>Error</AlertTitle>
  This is an error alert — check it out!
</Alert>

<Alert severity="warning">
  <AlertTitle>Warning</AlertTitle>
  This is a warning alert — check it out!
</Alert>

<Alert severity="info">
  <AlertTitle>Info</AlertTitle>
  This is an info alert — check it out!
</Alert>

<Alert severity="success">
  <AlertTitle>Success</AlertTitle>
  This is a success alert — check it out!
</Alert>
```