# Surface Components

Surface components provide Material Design elevation and content organization through Paper surfaces, expandable accordions, and informational badges and tooltips.

## Capabilities

### Paper

Basic surface component providing Material Design elevation and background styling.

```typescript { .api }
/**
 * Basic surface component with Material Design elevation
 * @param props - Paper component props
 * @returns JSX.Element - Paper component
 */
function Paper(props: PaperProps): JSX.Element;

interface PaperProps extends CommonProps {
  /** The component used for the root node */
  component?: React.ElementType;
  /** Shadow depth of component (0-24) */
  elevation?: number;
  /** If true, rounded corners are disabled */
  square?: boolean;
  /** The variant to use */
  variant?: 'elevation' | 'outlined';
  /** The content of the component */
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Paper } from "@mui/material";

// Basic paper with elevation
<Paper elevation={3}>
  <p>This content is displayed on a raised surface</p>
</Paper>

// Outlined paper variant
<Paper variant="outlined">
  <p>This content has an outline instead of shadow</p>
</Paper>

// Square paper without rounded corners
<Paper square elevation={1}>
  <p>Sharp corners paper</p>
</Paper>
```

### Accordion

Expandable panels for organizing content into collapsible sections.

```typescript { .api }
/**
 * Expandable panels for organizing content
 * @param props - Accordion component props
 * @returns JSX.Element - Accordion component
 */
function Accordion(props: AccordionProps): JSX.Element;

interface AccordionProps extends CommonProps {
  /** The content of the component */
  children?: React.ReactNode;
  /** If true, expands the accordion by default */
  defaultExpanded?: boolean;
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, it removes the margin between two expanded accordion items */
  disableGutters?: boolean;
  /** If true, expands the accordion, otherwise collapse it */
  expanded?: boolean;
  /** Callback fired when the expand/collapse state is changed */
  onChange?: (event: React.SyntheticEvent, expanded: boolean) => void;
  /** If true, rounded corners are disabled */
  square?: boolean;
  /** The component used for the transition */
  TransitionComponent?: React.ComponentType<any>;
  /** Props applied to the transition element */
  TransitionProps?: object;
}
```

### Accordion Summary

Header area of accordion with expand/collapse functionality.

```typescript { .api }
/**
 * Header area of accordion with expand/collapse
 * @param props - AccordionSummary component props
 * @returns JSX.Element - AccordionSummary component
 */
function AccordionSummary(props: AccordionSummaryProps): JSX.Element;

interface AccordionSummaryProps extends CommonProps {
  /** The content of the component */
  children?: React.ReactNode;
  /** The icon to display as the expand indicator */
  expandIcon?: React.ReactNode;
  /** This prop can help identify which element has keyboard focus */
  focusVisibleClassName?: string;
}
```

### Accordion Details

Content area of accordion that shows/hides based on expanded state.

```typescript { .api }
/**
 * Content area of accordion
 * @param props - AccordionDetails component props
 * @returns JSX.Element - AccordionDetails component
 */
function AccordionDetails(props: AccordionDetailsProps): JSX.Element;

interface AccordionDetailsProps extends CommonProps {
  /** The content of the component */
  children?: React.ReactNode;
}
```

### Accordion Actions

Container for accordion actions like buttons.

```typescript { .api }
/**
 * Container for accordion actions
 * @param props - AccordionActions component props
 * @returns JSX.Element - AccordionActions component
 */
function AccordionActions(props: AccordionActionsProps): JSX.Element;

interface AccordionActionsProps extends CommonProps {
  /** The content of the component */
  children?: React.ReactNode;
  /** If true, the actions do not have additional margin */
  disableSpacing?: boolean;
}
```

**Usage Examples:**

```typescript
import { 
  Accordion, 
  AccordionSummary, 
  AccordionDetails, 
  AccordionActions,
  Typography,
  Button
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

// Basic accordion
<Accordion>
  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
    <Typography>Accordion 1</Typography>
  </AccordionSummary>
  <AccordionDetails>
    <Typography>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    </Typography>
  </AccordionDetails>
</Accordion>

// Accordion with actions
<Accordion>
  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
    <Typography>Settings</Typography>
  </AccordionSummary>
  <AccordionDetails>
    <Typography>Configure your preferences here.</Typography>
  </AccordionDetails>
  <AccordionActions>
    <Button>Cancel</Button>
    <Button>Save</Button>
  </AccordionActions>
</Accordion>
```

### Badge

Component for displaying small amounts of data, typically numbers or status indicators.

```typescript { .api }
/**
 * Badge for displaying small amounts of data
 * @param props - Badge component props
 * @returns JSX.Element - Badge component
 */
function Badge(props: BadgeProps): JSX.Element;

interface BadgeProps extends CommonProps {
  /** The anchor of the badge */
  anchorOrigin?: {
    horizontal: 'left' | 'right';
    vertical: 'bottom' | 'top';
  };
  /** The content rendered within the badge */
  badgeContent?: React.ReactNode;
  /** The content rendered within the badge wrapper */
  children?: React.ReactNode;
  /** The color of the component */
  color?: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** The component used for the root node */
  component?: React.ElementType;
  /** If true, the badge is invisible */
  invisible?: boolean;
  /** Max count to show */
  max?: number;
  /** Wrapped shape the badge should overlap */
  overlap?: 'circular' | 'rectangular';
  /** Controls whether the badge is hidden when badgeContent is zero */
  showZero?: boolean;
  /** The variant to use */
  variant?: 'dot' | 'standard';
}
```

**Usage Examples:**

```typescript
import { Badge, Avatar, Icon } from "@mui/material";
import NotificationsIcon from "@mui/icons-material/Notifications";

// Basic badge with number
<Badge badgeContent={4} color="primary">
  <NotificationsIcon />
</Badge>

// Badge with maximum count
<Badge badgeContent={100} max={99} color="secondary">
  <NotificationsIcon />
</Badge>

// Dot badge
<Badge variant="dot" color="error">
  <Avatar src="/avatar.jpg" />
</Badge>
```

### Tooltip

Component for displaying additional information when hovering over or focusing on an element.

```typescript { .api }
/**
 * Tooltip for additional information
 * @param props - Tooltip component props
 * @returns JSX.Element - Tooltip component
 */
function Tooltip(props: TooltipProps): JSX.Element;

interface TooltipProps extends CommonProps {
  /** If true, adds an arrow to the tooltip */
  arrow?: boolean;
  /** Tooltip reference element */
  children: React.ReactElement;
  /** Do not respond to focus-visible events */
  disableFocusListener?: boolean;
  /** Do not respond to hover events */
  disableHoverListener?: boolean;
  /** Makes a tooltip not interactive */
  disableInteractive?: boolean;
  /** Do not respond to long press touch events */
  disableTouchListener?: boolean;
  /** The number of milliseconds to wait before showing the tooltip */
  enterDelay?: number;
  /** The number of milliseconds to wait before hiding the tooltip */
  leaveDelay?: number;
  /** Callback fired when the component is closed */
  onClose?: (event: React.SyntheticEvent) => void;
  /** Callback fired when the component is opened */
  onOpen?: (event: React.SyntheticEvent) => void;
  /** If true, the component is shown */
  open?: boolean;
  /** Tooltip placement */
  placement?: 'bottom-end' | 'bottom-start' | 'bottom' | 'left-end' | 'left-start' | 'left' | 'right-end' | 'right-start' | 'right' | 'top-end' | 'top-start' | 'top';
  /** Tooltip title. Zero-length titles string are never displayed */
  title: React.ReactNode;
  /** The component used for the transition */
  TransitionComponent?: React.ComponentType<any>;
  /** Props applied to the transition element */
  TransitionProps?: object;
}
```

**Usage Examples:**

```typescript
import { Tooltip, Button, IconButton } from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";

// Basic tooltip
<Tooltip title="Delete">
  <IconButton>
    <DeleteIcon />
  </IconButton>
</Tooltip>

// Tooltip with arrow and custom placement
<Tooltip title="Add" arrow placement="top">
  <Button>Hover me</Button>
</Tooltip>

// Controlled tooltip
<Tooltip title="Controlled tooltip" open={open}>
  <Button onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
    Controlled
  </Button>
</Tooltip>
```

## Common Types

```typescript { .api }
// Common props shared by surface components
interface CommonProps {
  className?: string;
  style?: React.CSSProperties;
  sx?: SxProps<Theme>;
}

// Anchor origin for badge positioning
interface AnchorOrigin {
  horizontal: 'left' | 'right';
  vertical: 'bottom' | 'top';
}

// Tooltip placement options
type TooltipPlacement = 
  | 'bottom-end' | 'bottom-start' | 'bottom'
  | 'left-end' | 'left-start' | 'left'
  | 'right-end' | 'right-start' | 'right'
  | 'top-end' | 'top-start' | 'top';
```