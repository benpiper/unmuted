# Data Display

Components for displaying data including lists, tables, cards, and typography with consistent styling.

## Capabilities

### Chip

Compact elements that represent an input, attribute, or action with optional delete functionality.

```typescript { .api }
/**
 * Compact elements that represent input, attribute, or action
 * @param props - Chip configuration
 * @returns Chip component
 */
function Chip(props: ChipProps): JSX.Element;

interface ChipProps extends CommonProps {
  /** The Avatar element to display */
  avatar?: React.ReactElement;
  /** If true, the chip will appear clickable */
  clickable?: boolean;
  /** The color of the component */
  color?: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** Override the default delete icon element */
  deleteIcon?: React.ReactElement;
  /** If true, the component is disabled */
  disabled?: boolean;
  /** Icon element */
  icon?: React.ReactElement;
  /** The content of the component */
  label?: React.ReactNode;
  /** Callback fired when the delete icon is clicked */
  onDelete?: React.EventHandler<any>;
  /** Callback fired when the chip is clicked */
  onClick?: React.EventHandler<React.MouseEvent>;
  /** The size of the Component */
  size?: 'small' | 'medium';
  /** The variant to use */
  variant?: 'filled' | 'outlined';
}
```

**Usage Examples:**

```typescript
import { Chip, Avatar } from "@mui/material";
import FaceIcon from "@mui/icons-material/Face";

// Basic chip
<Chip label="Basic chip" />

// Clickable chip
<Chip label="Clickable" onClick={() => console.log('clicked')} />

// Deletable chip
<Chip 
  label="Deletable" 
  onDelete={() => console.log('delete')}
/>

// Chip with avatar
<Chip
  avatar={<Avatar>M</Avatar>}
  label="With Avatar"
  variant="outlined"
/>

// Chip with icon
<Chip
  icon={<FaceIcon />}
  label="With Icon"
  color="primary"
/>
```

### Typography

Typography component for displaying text with Material Design typography scale.

```typescript { .api }
/**
 * Typography component for text display
 * @param props - Typography configuration
 * @returns Typography component
 */
function Typography(props: TypographyProps): JSX.Element;

interface TypographyProps extends CommonProps {
  /** Set the text-align on the component */
  align?: 'inherit' | 'left' | 'center' | 'right' | 'justify';
  /** The component used for the root node */
  component?: React.ElementType;
  /** If true, the text will have a bottom margin */
  gutterBottom?: boolean;
  /** If true, the text will not wrap, but instead will truncate with a text overflow ellipsis */
  noWrap?: boolean;
  /** If true, the text will have a paragraph styling */
  paragraph?: boolean;
  /** Applies the theme typography styles */
  variant?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'subtitle1' | 'subtitle2' | 'body1' | 'body2' | 'caption' | 'button' | 'overline' | 'inherit';
  children?: React.ReactNode;
}
```

### List

List component for displaying content in organized rows.

```typescript { .api }
/**
 * List component for displaying content in rows
 * @param props - List configuration
 * @returns List component
 */
function List(props: ListProps): JSX.Element;

/**
 * Individual list item
 * @param props - ListItem configuration
 * @returns ListItem component
 */
function ListItem(props: ListItemProps): JSX.Element;

/**
 * Text content for list items
 * @param props - ListItemText configuration
 * @returns ListItemText component
 */
function ListItemText(props: ListItemTextProps): JSX.Element;

interface ListProps extends CommonProps {
  /** If true, compact vertical padding designed for keyboard and mouse input is used for the list and list items */
  dense?: boolean;
  /** If true, vertical padding is removed from the list */
  disablePadding?: boolean;
  /** The content of the subheader, normally ListSubheader */
  subheader?: React.ReactNode;
  children?: React.ReactNode;
}

interface ListItemProps extends CommonProps {
  /** Defines the align-items style property */
  alignItems?: 'flex-start' | 'center';
  /** If true, the list item is focused during the first mount */
  autoFocus?: boolean;
  /** The component used for the root node */
  component?: React.ElementType;
  /** If true, compact vertical padding designed for keyboard and mouse input is used */
  dense?: boolean;
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, the left and right padding is removed */
  disableGutters?: boolean;
  /** If true, all padding is removed */
  disablePadding?: boolean;
  /** If true, a 1px light border is added to the bottom of the list item */
  divider?: boolean;
  /** The element to display at the end of ListItem */
  secondaryAction?: React.ReactNode;
  /** If true, the component is selected */
  selected?: boolean;
  children?: React.ReactNode;
}

interface ListItemTextProps extends CommonProps {
  /** If true, the children are formatted to use typography body1 instead of body2 */
  disableTypography?: boolean;
  /** If true, the children are indented */
  inset?: boolean;
  /** The main content element */
  primary?: React.ReactNode;
  /** These props will be forwarded to the primary typography component */
  primaryTypographyProps?: TypographyProps;
  /** The secondary content element */
  secondary?: React.ReactNode;
  /** These props will be forwarded to the secondary typography component */
  secondaryTypographyProps?: TypographyProps;
}
```

**Usage Examples:**

```typescript
import { 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  ListItemButton,
  Typography 
} from "@mui/material";
import InboxIcon from "@mui/icons-material/Inbox";

// Basic typography
<Typography variant="h1" gutterBottom>
  Main Heading
</Typography>
<Typography variant="body1" paragraph>
  This is a paragraph of body text using the Material Design typography scale.
</Typography>

// Simple list
<List>
  <ListItem>
    <ListItemText primary="Item 1" />
  </ListItem>
  <ListItem>
    <ListItemText primary="Item 2" secondary="Secondary text" />
  </ListItem>
</List>

// Interactive list with icons
<List>
  <ListItemButton>
    <ListItemIcon>
      <InboxIcon />
    </ListItemIcon>
    <ListItemText primary="Inbox" secondary="5 unread messages" />
  </ListItemButton>
</List>
```

**Additional List Components:**

```typescript { .api }
/**
 * Clickable list item component for interactive lists
 * @param props - ListItemButton configuration
 * @returns ListItemButton component
 */
function ListItemButton(props: ListItemButtonProps): JSX.Element;

/**
 * Icon container for list items
 * @param props - ListItemIcon configuration
 * @returns ListItemIcon component
 */
function ListItemIcon(props: ListItemIconProps): JSX.Element;

/**
 * Avatar container for list items
 * @param props - ListItemAvatar configuration
 * @returns ListItemAvatar component
 */
function ListItemAvatar(props: ListItemAvatarProps): JSX.Element;

/**
 * Secondary action area for list items
 * @param props - ListItemSecondaryAction configuration
 * @returns ListItemSecondaryAction component
 */
function ListItemSecondaryAction(props: ListItemSecondaryActionProps): JSX.Element;

/**
 * Subheader for list sections
 * @param props - ListSubheader configuration
 * @returns ListSubheader component
 */
function ListSubheader(props: ListSubheaderProps): JSX.Element;

interface ListItemButtonProps extends CommonProps {
  /** If true, the list item is focused during the first mount */
  autoFocus?: boolean;
  /** If true, the list item is disabled */
  disabled?: boolean;
  /** If true, compact vertical padding designed for keyboard and mouse input is used */
  dense?: boolean;
  /** If true, the left and right padding is removed */
  divider?: boolean;
  /** If true, the list item is selected */
  selected?: boolean;
  /** Callback fired when clicked */
  onClick?: (event: React.MouseEvent<HTMLDivElement>) => void;
  children?: React.ReactNode;
}

interface ListItemIconProps extends CommonProps {
  children?: React.ReactNode;
}

interface ListItemAvatarProps extends CommonProps {
  children?: React.ReactNode;
}

interface ListItemSecondaryActionProps extends CommonProps {
  children?: React.ReactNode;
}

interface ListSubheaderProps extends CommonProps {
  /** The color of the component */
  color?: 'default' | 'primary' | 'inherit';
  /** If true, the List Subheader will not have gutters */
  disableGutters?: boolean;
  /** If true, the List Subheader will be indented */
  inset?: boolean;
  /** If true, the List Subheader is displayed in a sticky position */
  disableSticky?: boolean;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { 
  List, 
  ListItemButton, 
  ListItemIcon, 
  ListItemText, 
  ListItemAvatar, 
  ListItemSecondaryAction, 
  ListSubheader,
  Avatar,
  IconButton
} from "@mui/material";
import { Inbox, Drafts, Delete } from "@mui/icons-material";

// List with subheaders and interactive buttons
<List>
  <ListSubheader>Recent Messages</ListSubheader>
  <ListItemButton>
    <ListItemAvatar>
      <Avatar>JD</Avatar>
    </ListItemAvatar>
    <ListItemText 
      primary="John Doe" 
      secondary="Hello, how are you doing today?" 
    />
    <ListItemSecondaryAction>
      <IconButton edge="end">
        <Delete />
      </IconButton>
    </ListItemSecondaryAction>
  </ListItemButton>
  
  <ListSubheader>Folders</ListSubheader>
  <ListItemButton>
    <ListItemIcon>
      <Inbox />
    </ListItemIcon>
    <ListItemText primary="Inbox" secondary="5 unread" />
  </ListItemButton>
  <ListItemButton>
    <ListItemIcon>
      <Drafts />
    </ListItemIcon>
    <ListItemText primary="Drafts" secondary="2 items" />
  </ListItemButton>
</List>
```

### Table

Table component for displaying tabular data with sorting and pagination support.

```typescript { .api }
/**
 * Table component for tabular data
 * @param props - Table configuration
 * @returns Table component
 */
function Table(props: TableProps): JSX.Element;

/**
 * Individual table cell
 * @param props - TableCell configuration
 * @returns TableCell component
 */
function TableCell(props: TableCellProps): JSX.Element;

/**
 * Table row component
 * @param props - TableRow configuration
 * @returns TableRow component
 */
function TableRow(props: TableRowProps): JSX.Element;

interface TableProps extends CommonProps {
  /** The component used for the root node */
  component?: React.ElementType;
  /** Allows TableCells to inherit size of the Table */
  padding?: 'normal' | 'checkbox' | 'none';
  /** Allows TableCells to inherit size of the Table */
  size?: 'small' | 'medium';
  /** Set the header sticky */
  stickyHeader?: boolean;
  children?: React.ReactNode;
}

interface TableCellProps extends CommonProps {
  /** Set the text-align on the table cell content */
  align?: 'inherit' | 'left' | 'center' | 'right' | 'justify';
  /** The component used for the root node */
  component?: React.ElementType;
  /** Sets the padding applied to the cell */
  padding?: 'normal' | 'checkbox' | 'none';
  /** Set scope attribute */
  scope?: string;
  /** Specify the size of the cell */
  size?: 'small' | 'medium';
  /** Set aria-sort direction */
  sortDirection?: 'asc' | 'desc' | false;
  /** Specify the cell type */
  variant?: 'head' | 'body' | 'footer';
  children?: React.ReactNode;
}

interface TableRowProps extends CommonProps {
  /** If true, the table row will shade on hover */
  hover?: boolean;
  /** If true, the table row will have the selected shading */
  selected?: boolean;
  children?: React.ReactNode;
}
```

**Additional Table Components:**

```typescript { .api }
/**
 * Container wrapper for table scroll behavior
 * @param props - TableContainer configuration
 * @returns TableContainer component
 */
function TableContainer(props: TableContainerProps): JSX.Element;

/**
 * Table header section grouping
 * @param props - TableHead configuration  
 * @returns TableHead component
 */
function TableHead(props: TableHeadProps): JSX.Element;

/**
 * Table body section grouping
 * @param props - TableBody configuration
 * @returns TableBody component
 */
function TableBody(props: TableBodyProps): JSX.Element;

/**
 * Table footer section grouping
 * @param props - TableFooter configuration
 * @returns TableFooter component
 */
function TableFooter(props: TableFooterProps): JSX.Element;

/**
 * Sortable column header with sort indicators
 * @param props - TableSortLabel configuration
 * @returns TableSortLabel component
 */
function TableSortLabel(props: TableSortLabelProps): JSX.Element;

/**
 * Pagination controls for tables
 * @param props - TablePagination configuration
 * @returns TablePagination component
 */
function TablePagination(props: TablePaginationProps): JSX.Element;

interface TableContainerProps extends CommonProps {
  /** The component used for the root node */
  component?: React.ElementType;
  children?: React.ReactNode;
}

interface TableHeadProps extends CommonProps {
  children?: React.ReactNode;
}

interface TableBodyProps extends CommonProps {
  children?: React.ReactNode;
}

interface TableFooterProps extends CommonProps {
  children?: React.ReactNode;
}

interface TableSortLabelProps extends CommonProps {
  /** If true, the label will be active (sorted) */
  active?: boolean;
  /** The sort direction */
  direction?: 'asc' | 'desc';
  /** Hide the sort icon when not active */
  hideSortIcon?: boolean;
  /** The icon to display when sorted ascending */
  iconDirection?: 'asc' | 'desc';
  /** Callback fired when the label is clicked */
  onClick?: (event: React.MouseEvent<HTMLSpanElement>) => void;
  children?: React.ReactNode;
}

interface TablePaginationProps extends CommonProps {
  /** Accepts a function which returns a string value that provides a user-friendly name for the current page */
  getItemAriaLabel?: (type: 'first' | 'last' | 'next' | 'previous') => string;
  /** Callback fired when the page is changed */
  onPageChange: (event: React.MouseEvent<HTMLButtonElement> | null, page: number) => void;
  /** Callback fired when the number of rows per page is changed */
  onRowsPerPageChange?: React.ChangeEventHandler<HTMLTextAreaElement | HTMLInputElement>;
  /** The zero-based index of the current page */
  page: number;
  /** The number of rows per page */
  rowsPerPage: number;
  /** Customizes the options of the rows per page select field */
  rowsPerPageOptions?: ReadonlyArray<number | { label: string; value: number }>;
  /** Customize the displayed rows label */
  labelRowsPerPage?: React.ReactNode;
  /** The total number of rows */
  count: number;
  /** The component used for displaying a select */
  SelectProps?: object;
}
```

**Usage Examples:**

```typescript
import { 
  Table, 
  TableContainer, 
  TableHead, 
  TableBody, 
  TableRow, 
  TableCell, 
  TableSortLabel, 
  TablePagination,
  Paper
} from "@mui/material";

// Complete table with sorting and pagination
<TableContainer component={Paper}>
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>
          <TableSortLabel
            active={orderBy === 'name'}
            direction={orderBy === 'name' ? order : 'asc'}
            onClick={() => handleSort('name')}
          >
            Name
          </TableSortLabel>
        </TableCell>
        <TableCell>Email</TableCell>
        <TableCell>Role</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {rows.map((row) => (
        <TableRow key={row.id} hover>
          <TableCell>{row.name}</TableCell>
          <TableCell>{row.email}</TableCell>
          <TableCell>{row.role}</TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
  <TablePagination
    component="div"
    count={totalRows}
    page={page}
    onPageChange={handlePageChange}
    rowsPerPage={rowsPerPage}
    onRowsPerPageChange={handleRowsPerPageChange}
    rowsPerPageOptions={[5, 10, 25]}
  />
</TableContainer>
```

### Card

Card component for containing related information and actions.

```typescript { .api }
/**
 * Card component for containing related information
 * @param props - Card configuration
 * @returns Card component
 */
function Card(props: CardProps): JSX.Element;

/**
 * Header section with avatar, title, and action
 * @param props - CardHeader configuration
 * @returns CardHeader component
 */
function CardHeader(props: CardHeaderProps): JSX.Element;

/**
 * Main content area of a card
 * @param props - CardContent configuration
 * @returns CardContent component
 */
function CardContent(props: CardContentProps): JSX.Element;

/**
 * Container for card actions
 * @param props - CardActions configuration
 * @returns CardActions component
 */
function CardActions(props: CardActionsProps): JSX.Element;

interface CardProps extends CommonProps {
  /** If true, the card will use raised styling */
  raised?: boolean;
  children?: React.ReactNode;
}

interface CardHeaderProps extends CommonProps {
  /** The action to display in the card header */
  action?: React.ReactNode;
  /** The Avatar element to display */
  avatar?: React.ReactNode;
  /** The component used for the root node */
  component?: React.ElementType;
  /** If true, subheader and title won't be wrapped by a Typography component */
  disableTypography?: boolean;
  /** The content of the component */
  subheader?: React.ReactNode;
  /** These props will be forwarded to the subheader */
  subheaderTypographyProps?: TypographyProps;
  /** The content of the component */
  title?: React.ReactNode;
  /** These props will be forwarded to the title */
  titleTypographyProps?: TypographyProps;
}

interface CardContentProps extends CommonProps {
  /** The component used for the root node */
  component?: React.ElementType;
  children?: React.ReactNode;
}

interface CardActionsProps extends CommonProps {
  /** If true, the actions do not have additional margin */
  disableSpacing?: boolean;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { 
  Card, 
  CardHeader, 
  CardContent, 
  CardActions, 
  Button, 
  Typography,
  Avatar 
} from "@mui/material";

// Basic card
<Card>
  <CardHeader
    avatar={<Avatar>R</Avatar>}
    title="Card Title"
    subheader="September 14, 2024"
  />
  <CardContent>
    <Typography variant="body2" color="text.secondary">
      This is the main content of the card. It can contain any information
      that needs to be displayed in a structured format.
    </Typography>
  </CardContent>
  <CardActions>
    <Button size="small">Learn More</Button>
    <Button size="small">Share</Button>
  </CardActions>
</Card>
```

### Avatar and Badge

Components for displaying user avatars and notification badges.

```typescript { .api }
/**
 * Avatar component for user photos, initials, or icons
 * @param props - Avatar configuration
 * @returns Avatar component
 */
function Avatar(props: AvatarProps): JSX.Element;

/**
 * Badge for displaying small amounts of data
 * @param props - Badge configuration
 * @returns Badge component
 */
function Badge(props: BadgeProps): JSX.Element;

interface AvatarProps extends CommonProps {
  /** Used in combination with src or srcSet to provide an alt attribute for the rendered img element */
  alt?: string;
  /** Used to render icon or text elements within the Avatar */
  children?: React.ReactNode;
  /** Attributes applied to the img element if the component is used to display an image */
  imgProps?: React.ImgHTMLAttributes<HTMLImageElement>;
  /** The sizes attribute for the img element */
  sizes?: string;
  /** The src attribute for the img element */
  src?: string;
  /** The srcSet attribute for the img element */
  srcSet?: string;
  /** The shape of the avatar */
  variant?: 'circular' | 'rounded' | 'square';
}

interface BadgeProps extends CommonProps {
  /** The anchor of the badge */
  anchorOrigin?: {
    vertical: 'top' | 'bottom';
    horizontal: 'left' | 'right';
  };
  /** The content rendered within the badge */
  badgeContent?: React.ReactNode;
  /** The color of the component */
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' | 'default';
  /** The component used for the root node */
  component?: React.ElementType;
  /** If true, the badge is invisible */
  invisible?: boolean;
  /** Max count to show */
  max?: number;
  /** Wrapped shape the badge should overlap */
  overlap?: 'rectangular' | 'circular';
  /** Controls whether the badge is hidden when badgeContent is zero */
  showZero?: boolean;
  /** The variant to use */
  variant?: 'standard' | 'dot';
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Avatar, Badge, AvatarGroup } from "@mui/material";
import { deepOrange, deepPurple } from "@mui/material/colors";

// Basic avatars
<Avatar alt="John Doe" src="/path/to/image.jpg" />
<Avatar sx={{ bgcolor: deepOrange[500] }}>JD</Avatar>
<Avatar sx={{ bgcolor: deepPurple[500] }}>
  <PersonIcon />
</Avatar>

// Avatar group
<AvatarGroup max={4}>
  <Avatar alt="User 1" src="/user1.jpg" />
  <Avatar alt="User 2" src="/user2.jpg" />
  <Avatar alt="User 3" src="/user3.jpg" />
  <Avatar alt="User 4" src="/user4.jpg" />
  <Avatar alt="User 5" src="/user5.jpg" />
</AvatarGroup>

// Badge with avatar
<Badge badgeContent={4} color="primary">
  <Avatar alt="User" src="/user.jpg" />
</Badge>
```

### ImageList

Components for displaying collections of images in a structured grid layout.

```typescript { .api }
/**
 * Image list for displaying a collection of images
 * @param props - ImageList configuration
 * @returns ImageList component
 */
function ImageList(props: ImageListProps): JSX.Element;

/**
 * Individual item in an image list
 * @param props - ImageListItem configuration
 * @returns ImageListItem component
 */
function ImageListItem(props: ImageListItemProps): JSX.Element;

/**
 * Bar overlay for image list items
 * @param props - ImageListItemBar configuration
 * @returns ImageListItemBar component
 */
function ImageListItemBar(props: ImageListItemBarProps): JSX.Element;

interface ImageListProps extends CommonProps {
  /** Number of columns */
  cols?: number;
  /** The component used for the root node */
  component?: React.ElementType;
  /** The gap between items in px */
  gap?: number;
  /** The height of one row in px */
  rowHeight?: number | 'auto';
  /** The variant to use */
  variant?: 'masonry' | 'quilted' | 'standard' | 'woven';
  children?: React.ReactNode;
}

interface ImageListItemProps extends CommonProps {
  /** Number of columns the item should span */
  cols?: number;
  /** The component used for the root node */
  component?: React.ElementType;
  /** Number of rows the item should span */
  rows?: number;
  children?: React.ReactNode;
}

interface ImageListItemBarProps extends CommonProps {
  /** An IconButton element to be used as secondary action target */
  actionIcon?: React.ReactNode;
  /** Position of secondary action IconButton */
  actionPosition?: 'left' | 'right';
  /** Position of the title bar */
  position?: 'below' | 'bottom' | 'top';
  /** String or element serving as subtitle */
  subtitle?: React.ReactNode;
  /** String or element serving as title */
  title?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { 
  ImageList, 
  ImageListItem, 
  ImageListItemBar,
  IconButton 
} from "@mui/material";
import InfoIcon from "@mui/icons-material/Info";

// Standard image list
<ImageList cols={3} rowHeight={164}>
  {itemData.map((item) => (
    <ImageListItem key={item.img}>
      <img
        src={`${item.img}?w=164&h=164&fit=crop&auto=format`}
        alt={item.title}
        loading="lazy"
      />
      <ImageListItemBar
        title={item.title}
        subtitle={item.author}
        actionIcon={
          <IconButton>
            <InfoIcon />
          </IconButton>
        }
      />
    </ImageListItem>
  ))}
</ImageList>

// Masonry image list
<ImageList variant="masonry" cols={3} gap={8}>
  {itemData.map((item) => (
    <ImageListItem key={item.img}>
      <img src={item.img} alt={item.title} loading="lazy" />
    </ImageListItem>
  ))}
</ImageList>
```

### Divider

Visual content separator for organizing sections and content.

```typescript { .api }
/**
 * Visual content separator for organizing sections and content
 * @param props - Divider configuration
 * @returns Divider component
 */
function Divider(props: DividerProps): JSX.Element;

interface DividerProps extends CommonProps {
  /** Absolutely position the element */
  absolute?: boolean;
  /** The component orientation */
  orientation?: 'horizontal' | 'vertical';
  /** If true, a vertical divider will have the correct height when used in flex container */
  flexItem?: boolean;
  /** If true, the divider will have a lighter color */
  light?: boolean;
  /** The text alignment */
  textAlign?: 'center' | 'left' | 'right';
  /** The variant to use */
  variant?: 'fullWidth' | 'inset' | 'middle';
  /** The content of the component */
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Divider, List, ListItem, ListItemText } from "@mui/material";

// Basic horizontal divider
<Divider />

// Divider with text
<Divider>OR</Divider>

// Vertical divider
<Divider orientation="vertical" flexItem />

// Divider with different variants
<Divider variant="inset" />
<Divider variant="middle" />

// Divider in a list
<List>
  <ListItem>
    <ListItemText primary="Item 1" />
  </ListItem>
  <Divider />
  <ListItem>
    <ListItemText primary="Item 2" />
  </ListItem>
</List>
```

### Icon

Component for displaying font icons and icon fonts.

```typescript { .api }
/**
 * Component for displaying font icons and icon fonts
 * @param props - Icon configuration
 * @returns Icon component
 */
function Icon(props: IconProps): JSX.Element;

interface IconProps extends CommonProps {
  /** The name of the icon font ligature */
  children?: React.ReactNode;
  /** The color of the component */
  color?: 'inherit' | 'action' | 'disabled' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** The fontSize applied to the icon */
  fontSize?: 'inherit' | 'large' | 'medium' | 'small';
  /** The base class name according to the icon font */
  baseClassName?: string;
}
```

**Usage Examples:**

```typescript
import { Icon } from "@mui/material";

// Material Icons font
<Icon>star</Icon>

// Font Awesome (with proper setup)
<Icon baseClassName="fas" className="fa-heart" />

// Different sizes
<Icon fontSize="small">home</Icon>
<Icon fontSize="large">settings</Icon>

// Different colors
<Icon color="primary">favorite</Icon>
<Icon color="error">error</Icon>
```

### SvgIcon

Wrapper component for displaying SVG icons with Material-UI styling.

```typescript { .api }
/**
 * Wrapper component for displaying SVG icons with Material-UI styling
 * @param props - SvgIcon configuration
 * @returns SvgIcon component
 */
function SvgIcon(props: SvgIconProps): JSX.Element;

interface SvgIconProps extends CommonProps {
  /** The color of the component */
  color?: 'inherit' | 'action' | 'disabled' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** The fontSize applied to the icon */
  fontSize?: 'inherit' | 'large' | 'medium' | 'small';
  /** Applies a color attribute to the SVG element */
  htmlColor?: string;
  /** If true, the root node will inherit the custom component's viewBox */
  inheritViewBox?: boolean;
  /** The shape-rendering attribute */
  shapeRendering?: string;
  /** The title attribute for accessibility */
  titleAccess?: string;
  /** Allows you to redefine what the coordinates without units mean inside an SVG element */
  viewBox?: string;
  /** SVG path or element content */
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { SvgIcon } from "@mui/material";

// Custom SVG icon
<SvgIcon>
  <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
</SvgIcon>

// Custom icon with color
<SvgIcon color="primary">
  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
</SvgIcon>

// Custom icon component
function HomeIcon(props) {
  return (
    <SvgIcon {...props}>
      <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
    </SvgIcon>
  );
}

<HomeIcon color="action" />
```

### AvatarGroup

Component for displaying multiple avatars in a group with overflow management.

```typescript { .api }
/**
 * Component for displaying multiple avatars in a group with overflow management
 * @param props - AvatarGroup configuration
 * @returns AvatarGroup component
 */
function AvatarGroup(props: AvatarGroupProps): JSX.Element;

interface AvatarGroupProps extends CommonProps {
  /** The avatars to render */
  children?: React.ReactNode;
  /** Max avatars to show before +x indicator */
  max?: number;
  /** Spacing between avatars */
  spacing?: number | string;
  /** The total number of avatars (for +x calculation) */
  total?: number;
  /** The variant to use for the avatars */
  variant?: 'circular' | 'rounded' | 'square';
}
```

**Usage Examples:**

```typescript
import { AvatarGroup, Avatar } from "@mui/material";

// Basic avatar group
<AvatarGroup max={4}>
  <Avatar alt="Remy Sharp" src="/avatars/1.jpg" />
  <Avatar alt="Travis Howard" src="/avatars/2.jpg" />
  <Avatar alt="Cindy Baker" src="/avatars/3.jpg" />
  <Avatar alt="Agnes Walker" src="/avatars/4.jpg" />
  <Avatar alt="Trevor Henderson" src="/avatars/5.jpg" />
</AvatarGroup>

// Avatar group with total count
<AvatarGroup max={3} total={24}>
  <Avatar alt="Remy Sharp" src="/avatars/1.jpg" />
  <Avatar alt="Travis Howard" src="/avatars/2.jpg" />
  <Avatar alt="Cindy Baker" src="/avatars/3.jpg" />
</AvatarGroup>

// Avatar group with custom spacing
<AvatarGroup max={4} spacing="medium">
  <Avatar>H</Avatar>
  <Avatar>O</Avatar>
  <Avatar>P</Avatar>
  <Avatar>E</Avatar>
</AvatarGroup>
```