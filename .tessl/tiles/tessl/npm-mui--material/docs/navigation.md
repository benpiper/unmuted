# Navigation Components

Navigation elements including app bars, drawers, menus, tabs, and breadcrumbs for application structure.

## Capabilities

### AppBar

Application bar component for navigation and branding, typically positioned at the top of the application.

```typescript { .api }
/**
 * Application bar for navigation and branding
 * @param props - AppBar configuration
 * @returns AppBar component
 */
function AppBar(props: AppBarProps): JSX.Element;

interface AppBarProps extends CommonProps {
  /** The positioning type */
  position?: 'fixed' | 'absolute' | 'sticky' | 'static' | 'relative';
  /** The color of the component */
  color?: 'default' | 'inherit' | 'primary' | 'secondary' | 'transparent';
  /** If true, the color prop is applied in dark mode */
  enableColorOnDark?: boolean;
  /** The component used for the root node */
  component?: React.ElementType;
  children?: React.ReactNode;
}
```

### Toolbar

Flexible toolbar component, often used within AppBar for organizing navigation elements.

```typescript { .api }
/**
 * Flexible toolbar component
 * @param props - Toolbar configuration
 * @returns Toolbar component
 */
function Toolbar(props: ToolbarProps): JSX.Element;

interface ToolbarProps extends CommonProps {
  /** The variant to use */
  variant?: 'regular' | 'dense';
  /** If true, the left and right padding is removed */
  disableGutters?: boolean;
  /** The component used for the root node */
  component?: React.ElementType;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { AppBar, Toolbar, Typography, Button, IconButton } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";

// Basic app bar
<AppBar position="static">
  <Toolbar>
    <IconButton edge="start" color="inherit" aria-label="menu">
      <MenuIcon />
    </IconButton>
    <Typography variant="h6" sx={{ flexGrow: 1 }}>
      My Application
    </Typography>
    <Button color="inherit">Login</Button>
  </Toolbar>
</AppBar>

// Fixed app bar with elevation
<AppBar position="fixed" elevation={4}>
  <Toolbar>
    <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
      Fixed Header
    </Typography>
  </Toolbar>
</AppBar>
```

### Drawer

Navigation drawer panel that slides in from the side of the screen.

```typescript { .api }
/**
 * Navigation drawer panel
 * @param props - Drawer configuration
 * @returns Drawer component
 */
function Drawer(props: DrawerProps): JSX.Element;

interface DrawerProps extends CommonProps {
  /** Side from which the drawer will appear */
  anchor?: 'left' | 'top' | 'right' | 'bottom';
  /** If true, the drawer is open */
  open?: boolean;
  /** The variant to use */
  variant?: 'permanent' | 'persistent' | 'temporary';
  /** Callback fired when the component requests to be closed */
  onClose?: (event: React.SyntheticEvent) => void;
  /** Props applied to the Modal element */
  ModalProps?: Partial<ModalProps>;
  /** Props applied to the Paper element */
  PaperProps?: Partial<PaperProps>;
  /** Props applied to the Slide transition element */
  SlideProps?: Partial<SlideProps>;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Drawer, List, ListItem, ListItemText, Divider } from "@mui/material";

// Temporary drawer
<Drawer
  anchor="left"
  open={drawerOpen}
  onClose={handleDrawerClose}
>
  <List>
    <ListItem button>
      <ListItemText primary="Home" />
    </ListItem>
    <ListItem button>
      <ListItemText primary="About" />
    </ListItem>
    <Divider />
    <ListItem button>
      <ListItemText primary="Contact" />
    </ListItem>
  </List>
</Drawer>

// Permanent drawer
<Drawer
  variant="permanent"
  sx={{
    width: 240,
    flexShrink: 0,
    '& .MuiDrawer-paper': {
      width: 240,
      boxSizing: 'border-box',
    },
  }}
>
  <Toolbar />
  <List>
    <ListItem button>
      <ListItemText primary="Dashboard" />
    </ListItem>
    <ListItem button>
      <ListItemText primary="Settings" />
    </ListItem>
  </List>
</Drawer>
```

### Tabs

Tab navigation component for organizing content into separate views.

```typescript { .api }
/**
 * Tab navigation component
 * @param props - Tabs configuration
 * @returns Tabs component
 */
function Tabs(props: TabsProps): JSX.Element;

/**
 * Individual tab component
 * @param props - Tab configuration
 * @returns Tab component
 */
function Tab(props: TabProps): JSX.Element;

interface TabsProps extends CommonProps {
  /** Callback fired when the value changes */
  onChange?: (event: React.SyntheticEvent, value: any) => void;
  /** The value of the currently selected Tab */
  value?: any;
  /** The tabs orientation */
  orientation?: 'horizontal' | 'vertical';
  /** The component orientation */
  variant?: 'standard' | 'scrollable' | 'fullWidth';
  /** Determines the color of the indicator */
  indicatorColor?: 'primary' | 'secondary';
  /** Determines the color of the Tab */
  textColor?: 'primary' | 'secondary' | 'inherit';
  /** If true, the tabs are centered */
  centered?: boolean;
  /** Determine behavior of scroll buttons when tabs are set to scroll */
  scrollButtons?: 'auto' | 'desktop' | 'on' | 'off';
  /** If true, the scrollbar is visible */
  visibleScrollbar?: boolean;
  /** If true, keyboard focus will wrap around */
  allowScrollButtonsMobile?: boolean;
  children?: React.ReactNode;
}

interface TabProps extends CommonProps {
  /** The label element */
  label?: React.ReactNode;
  /** The icon element */
  icon?: React.ReactNode;
  /** The position of the icon relative to the label */
  iconPosition?: 'start' | 'end' | 'top' | 'bottom';
  /** If true, the tab is disabled */
  disabled?: boolean;
  /** You can wrap a string in an object with the 'wrapped' property to make the Tab fit */
  wrapped?: boolean;
  /** The value to associate with the tab */
  value?: any;
  /** Tab index value */
  tabIndex?: number;
  /** If true, the ripple effect is disabled */
  disableRipple?: boolean;
  /** If true, the focus ripple is disabled */
  disableFocusRipple?: boolean;
  /** The component used for the root node */
  component?: React.ElementType;
}
```

**Usage Examples:**

```typescript
import { Tabs, Tab, TabPanel, Box } from "@mui/material";

function TabPanel({ children, value, index, ...other }: TabPanelProps) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

// Basic tabs
<Box sx={{ width: '100%' }}>
  <Tabs value={tabValue} onChange={handleTabChange}>
    <Tab label="Overview" />
    <Tab label="Details" />
    <Tab label="Settings" />
  </Tabs>
  
  <TabPanel value={tabValue} index={0}>
    Overview content
  </TabPanel>
  <TabPanel value={tabValue} index={1}>
    Details content
  </TabPanel>
  <TabPanel value={tabValue} index={2}>
    Settings content
  </TabPanel>
</Box>

// Tabs with icons
<Tabs value={tabValue} onChange={handleTabChange}>
  <Tab icon={<HomeIcon />} label="Home" />
  <Tab icon={<FavoriteIcon />} label="Favorites" />
  <Tab icon={<PersonIcon />} label="Profile" />
</Tabs>
```

### Menu

Menu component for displaying a list of choices to the user.

```typescript { .api }
/**
 * Menu component for displaying choices
 * @param props - Menu configuration
 * @returns Menu component
 */
function Menu(props: MenuProps): JSX.Element;

/**
 * Individual menu item
 * @param props - MenuItem configuration
 * @returns MenuItem component
 */
function MenuItem(props: MenuItemProps): JSX.Element;

interface MenuProps extends CommonProps {
  /** An HTML element, or a function that returns one */
  anchorEl?: null | Element | ((element: Element) => Element);
  /** The anchor reference type */
  anchorReference?: 'anchorEl' | 'anchorPosition' | 'none';
  /** The anchor position */
  anchorPosition?: { top?: number; left?: number };
  /** This is the point on the anchor where the popover's anchorEl will attach to */
  anchorOrigin?: PopoverOrigin;
  /** If true, the menu will be focused on open */
  autoFocus?: boolean;
  /** Menu contents, normally MenuItems */
  children?: React.ReactNode;
  /** Props applied to the MenuList element */
  MenuListProps?: Partial<MenuListProps>;
  /** Callback fired when the component requests to be closed */
  onClose?: (event: React.SyntheticEvent) => void;
  /** If true, the menu is visible */
  open: boolean;
  /** This is the point on the popover which will attach to the anchor's origin */
  transformOrigin?: PopoverOrigin;
  /** The variant to use */
  variant?: 'menu' | 'selectedMenu';
}

interface MenuItemProps extends CommonProps {
  /** If true, the menu item will be auto-focused when the menu opens */
  autoFocus?: boolean;
  /** The component used for the root node */
  component?: React.ElementType;
  /** If true, compact vertical padding designed for keyboard and mouse input is used */
  dense?: boolean;
  /** If true, the left and right padding is removed */
  disableGutters?: boolean;
  /** If true, the menu item is disabled */
  disabled?: boolean;
  /** If true, a 1px light border is added to the bottom of the menu item */
  divider?: boolean;
  /** This prop can help identify which element has keyboard focus */
  focusVisibleClassName?: string;
  /** If true, the menu item is selected */
  selected?: boolean;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Menu, MenuItem, IconButton } from "@mui/material";
import MoreVertIcon from "@mui/icons-material/MoreVert";

function DropdownMenu() {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <>
      <IconButton onClick={handleClick}>
        <MoreVertIcon />
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleClose}>Profile</MenuItem>
        <MenuItem onClick={handleClose}>Settings</MenuItem>
        <MenuItem onClick={handleClose}>Logout</MenuItem>
      </Menu>
    </>
  );
}
```

### Breadcrumbs

Navigation breadcrumbs component showing the current page's location within a hierarchy.

```typescript { .api }
/**
 * Navigation breadcrumbs component
 * @param props - Breadcrumbs configuration
 * @returns Breadcrumbs component
 */
function Breadcrumbs(props: BreadcrumbsProps): JSX.Element;

interface BreadcrumbsProps extends CommonProps {
  /** The breadcrumb children */
  children?: React.ReactNode;
  /** Custom separator for the breadcrumbs */
  separator?: React.ReactNode;
  /** Specifies the maximum number of breadcrumbs to display */
  maxItems?: number;
  /** The number of items to show before the ellipsis */
  itemsBeforeCollapse?: number;
  /** The number of items to show after the ellipsis */
  itemsAfterCollapse?: number;
  /** Override the default label for the expand button */
  expandText?: string;
}
```

**Usage Examples:**

```typescript
import { Breadcrumbs, Link, Typography } from "@mui/material";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";

// Basic breadcrumbs
<Breadcrumbs aria-label="breadcrumb">
  <Link color="inherit" href="/">
    Home
  </Link>
  <Link color="inherit" href="/products">
    Products
  </Link>
  <Typography color="text.primary">Electronics</Typography>
</Breadcrumbs>

// Custom separator
<Breadcrumbs separator={<NavigateNextIcon fontSize="small" />}>
  <Link color="inherit" href="/">
    Home
  </Link>
  <Link color="inherit" href="/category">
    Category
  </Link>
  <Typography color="text.primary">Current Page</Typography>
</Breadcrumbs>
```

### Stepper

Multi-step navigation components for wizards and process flows.

```typescript { .api }
/**
 * Container for step navigation
 * @param props - Stepper configuration
 * @returns Stepper component
 */
function Stepper(props: StepperProps): JSX.Element;

/**
 * Individual step in a stepper
 * @param props - Step configuration
 * @returns Step component
 */
function Step(props: StepProps): JSX.Element;

/**
 * Label and optional icon for a step
 * @param props - StepLabel configuration
 * @returns StepLabel component
 */
function StepLabel(props: StepLabelProps): JSX.Element;

/**
 * Content area for a step
 * @param props - StepContent configuration
 * @returns StepContent component
 */
function StepContent(props: StepContentProps): JSX.Element;

interface StepperProps extends CommonProps {
  /** Set the active step (zero based index) */
  activeStep?: number;
  /** If set to 'true' and orientation is horizontal, the linear stepper will allow the user to navigate between steps in any order */
  nonLinear?: boolean;
  /** The component orientation */
  orientation?: 'horizontal' | 'vertical';
  children?: React.ReactNode;
}

interface StepProps extends CommonProps {
  /** Sets the step as active */
  active?: boolean;
  /** Mark the step as completed */
  completed?: boolean;
  /** If true, the step is disabled */
  disabled?: boolean;
  /** The optional node to display */
  optional?: React.ReactNode;
  children?: React.ReactNode;
}

interface StepLabelProps extends CommonProps {
  /** In most cases will simply be a string containing a title for the label */
  children?: React.ReactNode;
  /** The props used for the error icon */
  error?: boolean;
  /** Override the default label of the step icon */
  icon?: React.ReactNode;
  /** The optional node to display */
  optional?: React.ReactNode;
  /** The component to render in place of the StepIcon */
  StepIconComponent?: React.ElementType;
  /** Props applied to the StepIcon element */
  StepIconProps?: object;
}

interface StepContentProps extends CommonProps {
  /** The content of the component */
  children?: React.ReactNode;
  /** The component used for the transition */
  TransitionComponent?: React.ComponentType<any>;
  /** Props applied to the transition element */
  TransitionProps?: object;
}
```

### MobileStepper

Compact stepper designed for mobile interfaces.

```typescript { .api }
/**
 * Compact stepper for mobile interfaces
 * @param props - MobileStepper configuration
 * @returns MobileStepper component
 */
function MobileStepper(props: MobileStepperProps): JSX.Element;

interface MobileStepperProps extends CommonProps {
  /** Set the active step (zero based index) */
  activeStep: number;
  /** A back button element */
  backButton: React.ReactNode;
  /** A next button element */
  nextButton: React.ReactNode;
  /** The total steps */
  steps: number;
  /** The variant to use */
  variant?: 'text' | 'dots' | 'progress';
  /** Props applied to the LinearProgress element */
  LinearProgressProps?: object;
  /** The positioning type */
  position?: 'bottom' | 'static' | 'top';
}
```

### Pagination

Pagination component for navigating through multiple pages of content.

```typescript { .api }
/**
 * Pagination component for page navigation
 * @param props - Pagination configuration
 * @returns Pagination component
 */
function Pagination(props: PaginationProps): JSX.Element;

/**
 * Individual pagination item
 * @param props - PaginationItem configuration
 * @returns PaginationItem component
 */
function PaginationItem(props: PaginationItemProps): JSX.Element;

interface PaginationProps extends CommonProps {
  /** Number of always visible pages at the beginning and end */
  boundaryCount?: number;
  /** The active page */
  page?: number;
  /** The total number of pages */
  count?: number;
  /** The default page selected */
  defaultPage?: number;
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, hide the next-page button */
  hideNextButton?: boolean;
  /** If true, hide the previous-page button */
  hidePrevButton?: boolean;
  /** Callback fired when the page is changed */
  onChange?: (event: React.ChangeEvent<unknown>, page: number) => void;
  /** Render the item */
  renderItem?: (item: PaginationRenderItemParams) => React.ReactNode;
  /** The shape of the pagination items */
  shape?: 'circular' | 'rounded';
  /** Number of always visible pages before and after the current page */
  siblingCount?: number;
  /** The size of the component */
  size?: 'small' | 'medium' | 'large';
  /** The variant to use */
  variant?: 'outlined' | 'text';
}

interface PaginationItemProps extends CommonProps {
  /** The current page number */
  page?: number;
  /** If true, the item is selected */
  selected?: boolean;
  /** The shape of the pagination item */
  shape?: 'circular' | 'rounded';
  /** The size of the component */
  size?: 'small' | 'medium' | 'large';
  /** The type of pagination item */
  type?: 'page' | 'first' | 'last' | 'next' | 'previous' | 'start-ellipsis' | 'end-ellipsis';
  /** The variant to use */
  variant?: 'outlined' | 'text';
}
```

**Usage Examples:**

```typescript
import {
  Stepper,
  Step,
  StepLabel,
  StepContent,
  MobileStepper,
  Pagination,
  Button,
  Typography,
  Box
} from "@mui/material";
import KeyboardArrowLeft from "@mui/icons-material/KeyboardArrowLeft";
import KeyboardArrowRight from "@mui/icons-material/KeyboardArrowRight";

const steps = ['Select campaign settings', 'Create an ad group', 'Create an ad'];

// Horizontal stepper
<Stepper activeStep={1}>
  {steps.map((label, index) => (
    <Step key={label}>
      <StepLabel>{label}</StepLabel>
    </Step>
  ))}
</Stepper>

// Vertical stepper with content
<Stepper orientation="vertical" activeStep={1}>
  {steps.map((label, index) => (
    <Step key={label}>
      <StepLabel>{label}</StepLabel>
      <StepContent>
        <Typography>Content for {label}</Typography>
        <Box sx={{ mb: 2 }}>
          <Button variant="contained" sx={{ mt: 1, mr: 1 }}>
            Continue
          </Button>
          <Button disabled={index === 0} sx={{ mt: 1, mr: 1 }}>
            Back
          </Button>
        </Box>
      </StepContent>
    </Step>
  ))}
</Stepper>

// Mobile stepper
<MobileStepper
  steps={6}
  position="static"
  activeStep={activeStep}
  nextButton={
    <Button size="small" onClick={handleNext} disabled={activeStep === 5}>
      Next
      <KeyboardArrowRight />
    </Button>
  }
  backButton={
    <Button size="small" onClick={handleBack} disabled={activeStep === 0}>
      <KeyboardArrowLeft />
      Back
    </Button>
  }
/>

// Pagination
<Pagination 
  count={10} 
  page={page} 
  onChange={handleChange} 
  color="primary" 
/>
```

## Navigation Layout Patterns

### App Shell with Navigation

```typescript
import {
  AppBar,
  Toolbar,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
  IconButton,
  Box
} from "@mui/material";
import {
  Menu as MenuIcon,
  Home as HomeIcon,
  Settings as SettingsIcon,
  Person as PersonIcon
} from "@mui/icons-material";

const drawerWidth = 240;

function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <Box>
      <Toolbar />
      <List>
        <ListItem button>
          <ListItemIcon>
            <HomeIcon />
          </ListItemIcon>
          <ListItemText primary="Home" />
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <PersonIcon />
          </ListItemIcon>
          <ListItemText primary="Profile" />
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            My Application
          </Typography>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` }
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
}
```

### Link

Component for navigation links with Material-UI styling and router integration.

```typescript { .api }
/**
 * Component for navigation links with Material-UI styling and router integration
 * @param props - Link configuration
 * @returns Link component
 */
function Link(props: LinkProps): JSX.Element;

interface LinkProps extends CommonProps {
  /** The color of the link */
  color?: 'inherit' | 'primary' | 'secondary' | 'textPrimary' | 'textSecondary' | 'error';
  /** Controls when the link should have an underline */
  underline?: 'none' | 'hover' | 'always';
  /** The variant to use */
  variant?: 'inherit' | 'body1' | 'body2' | 'button' | 'caption' | 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'overline' | 'subtitle1' | 'subtitle2';
  /** The URL to link to */
  href?: string;
  /** The content of the link */
  children?: React.ReactNode;
  /** The component used for the root node */
  component?: React.ElementType;
  /** Callback fired when the link is clicked */
  onClick?: (event: React.MouseEvent<HTMLElement>) => void;
}
```

**Usage Examples:**

```typescript
import { Link, Typography } from "@mui/material";

// Basic link
<Link href="/about">About Us</Link>

// Link with different colors
<Link href="/contact" color="secondary">
  Contact
</Link>

// Link without underline
<Link href="/services" underline="none">
  Services
</Link>

// Link with typography variant
<Link href="/blog" variant="h6">
  Blog
</Link>

// Link as button component
<Link component="button" onClick={() => console.log('clicked')}>
  Click me
</Link>
```

### MenuList

Component for displaying a list of menu items with keyboard navigation.

```typescript { .api }
/**
 * Component for displaying a list of menu items with keyboard navigation
 * @param props - MenuList configuration
 * @returns MenuList component
 */
function MenuList(props: MenuListProps): JSX.Element;

interface MenuListProps extends CommonProps {
  /** If true, will focus the first item if autoFocus is true */
  autoFocus?: boolean;
  /** If true, will focus the first item */
  autoFocusItem?: boolean;
  /** If true, will not apply focus outline */
  disabledItemsFocusable?: boolean;
  /** If true, will disable list item focus on keyboard navigation */
  disableListWrap?: boolean;
  /** MenuList contents */
  children?: React.ReactNode;
  /** The variant to use */
  variant?: 'menu' | 'selectedMenu';
}
```

**Usage Examples:**

```typescript
import { MenuList, MenuItem, ListItemText, ListItemIcon, Divider } from "@mui/material";
import { Send, Drafts, Inbox } from "@mui/icons-material";

// Basic menu list
<MenuList>
  <MenuItem>
    <ListItemIcon>
      <Send fontSize="small" />
    </ListItemIcon>
    <ListItemText>Sent mail</ListItemText>
  </MenuItem>
  <MenuItem>
    <ListItemIcon>
      <Drafts fontSize="small" />
    </ListItemIcon>
    <ListItemText>Drafts</ListItemText>
  </MenuItem>
  <Divider />
  <MenuItem>
    <ListItemIcon>
      <Inbox fontSize="small" />
    </ListItemIcon>
    <ListItemText>Inbox</ListItemText>
  </MenuItem>
</MenuList>

// Menu list with auto focus
<MenuList autoFocusItem>
  <MenuItem>Profile</MenuItem>
  <MenuItem>My account</MenuItem>
  <MenuItem>Logout</MenuItem>
</MenuList>
```

### BottomNavigation

Navigation component for mobile interfaces with action buttons at the bottom.

```typescript { .api }
/**
 * Navigation component for mobile interfaces with action buttons at the bottom
 * @param props - BottomNavigation configuration
 * @returns BottomNavigation component
 */
function BottomNavigation(props: BottomNavigationProps): JSX.Element;

interface BottomNavigationProps extends CommonProps {
  /** Callback fired when the value changes */
  onChange?: (event: React.SyntheticEvent, value: any) => void;
  /** If true, all BottomNavigationActions will show their labels */
  showLabels?: boolean;
  /** The value of the currently selected BottomNavigationAction */
  value?: any;
  /** The content of the component */
  children?: React.ReactNode;
}
```

### BottomNavigationAction

Individual action component for BottomNavigation.

```typescript { .api }
/**
 * Individual action component for BottomNavigation
 * @param props - BottomNavigationAction configuration
 * @returns BottomNavigationAction component
 */
function BottomNavigationAction(props: BottomNavigationActionProps): JSX.Element;

interface BottomNavigationActionProps extends CommonProps {
  /** The icon to display */
  icon?: React.ReactNode;
  /** The label element */
  label?: React.ReactNode;
  /** If true, the BottomNavigationAction will show its label */
  showLabel?: boolean;
  /** You can provide your own value */
  value?: any;
}
```

**Usage Examples:**

```typescript
import { BottomNavigation, BottomNavigationAction } from "@mui/material";
import { Restore, Favorite, LocationOn } from "@mui/icons-material";

const [value, setValue] = React.useState(0);

<BottomNavigation
  value={value}
  onChange={(event, newValue) => {
    setValue(newValue);
  }}
  showLabels
>
  <BottomNavigationAction label="Recents" icon={<Restore />} />
  <BottomNavigationAction label="Favorites" icon={<Favorite />} />
  <BottomNavigationAction label="Nearby" icon={<LocationOn />} />
</BottomNavigation>
```