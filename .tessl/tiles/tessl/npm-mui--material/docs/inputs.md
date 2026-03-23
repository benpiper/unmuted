# Input Controls

Interactive input components including buttons, sliders, switches, and advanced controls like autocomplete.

## Capabilities

### Button

Button component with multiple variants, sizes, and states.

```typescript { .api }
/**
 * Button with multiple variants and states
 * @param props - Button configuration
 * @returns Button component
 */
function Button(props: ButtonProps): JSX.Element;

interface ButtonProps extends CommonProps {
  /** The color of the component */
  color?: 'inherit' | 'primary' | 'secondary' | 'success' | 'error' | 'info' | 'warning';
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, no elevation is used */
  disableElevation?: boolean;
  /** Element placed after the children */
  endIcon?: React.ReactNode;
  /** If true, the button will take up the full width of its container */
  fullWidth?: boolean;
  /** The URL to link to when the button is clicked */
  href?: string;
  /** If true, the button is in loading state */
  loading?: boolean;
  /** Element to display when loading is true */
  loadingIndicator?: React.ReactNode;
  /** The size of the component */
  size?: 'small' | 'medium' | 'large';
  /** Element placed before the children */
  startIcon?: React.ReactNode;
  /** The variant to use */
  variant?: 'text' | 'outlined' | 'contained';
  /** Callback fired when the button is clicked */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Button, Stack } from "@mui/material";
import SaveIcon from "@mui/icons-material/Save";

// Basic buttons
<Stack direction="row" spacing={2}>
  <Button variant="text">Text Button</Button>
  <Button variant="outlined">Outlined Button</Button>
  <Button variant="contained">Contained Button</Button>
</Stack>

// Button with icons
<Button
  variant="contained"
  startIcon={<SaveIcon />}
  onClick={handleSave}
>
  Save Document
</Button>

// Loading button
<Button
  variant="contained"
  loading={isLoading}
  loadingIndicator="Saving..."
  onClick={handleSubmit}
>
  Submit Form
</Button>
```

### Slider

Slider component for selecting values from a range.

```typescript { .api }
/**
 * Slider for selecting values from range
 * @param props - Slider configuration
 * @returns Slider component
 */
function Slider(props: SliderProps): JSX.Element;

interface SliderProps extends CommonProps {
  /** The color of the component */
  color?: 'primary' | 'secondary';
  /** The default value */
  defaultValue?: number | number[];
  /** If true, the component is disabled */
  disabled?: boolean;
  /** Marks indicate predetermined values */
  marks?: boolean | Mark[];
  /** The maximum allowed value */
  max?: number;
  /** The minimum allowed value */
  min?: number;
  /** Callback when the slider's value changed */
  onChange?: (event: Event, value: number | number[], activeThumb: number) => void;
  /** Callback when the mouseup is triggered */
  onChangeCommitted?: (event: React.SyntheticEvent | Event, value: number | number[]) => void;
  /** The component orientation */
  orientation?: 'horizontal' | 'vertical';
  /** The size of the slider */
  size?: 'small' | 'medium';
  /** The granularity step */
  step?: number | null;
  /** The value of the slider */
  value?: number | number[];
  /** Controls when the value label is displayed */
  valueLabelDisplay?: 'on' | 'auto' | 'off';
}

interface Mark {
  value: number;
  label?: React.ReactNode;
}
```

### Switch

Switch toggle control for binary states.

```typescript { .api }
/**
 * Switch toggle control
 * @param props - Switch configuration
 * @returns Switch component
 */
function Switch(props: SwitchProps): JSX.Element;

interface SwitchProps extends CommonProps {
  /** If true, the component is checked */
  checked?: boolean;
  /** The color of the component */
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' | 'default';
  /** The default checked state */
  defaultChecked?: boolean;
  /** If true, the component is disabled */
  disabled?: boolean;
  /** Callback fired when the state is changed */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>, checked: boolean) => void;
  /** The size of the component */
  size?: 'small' | 'medium';
  /** The value of the component */
  value?: unknown;
}
```

### Autocomplete

Autocomplete input component with suggestions and filtering.

```typescript { .api }
/**
 * Autocomplete input with suggestions
 * @param props - Autocomplete configuration
 * @returns Autocomplete component
 */
function Autocomplete<T>(props: AutocompleteProps<T>): JSX.Element;

interface AutocompleteProps<T> extends CommonProps {
  /** Array of options */
  options: T[];
  /** The value of the autocomplete */
  value?: T | T[] | null;
  /** Callback fired when the value changes */
  onChange?: (event: React.SyntheticEvent, value: T | T[] | null) => void;
  /** Callback fired when the input value changes */
  onInputChange?: (event: React.SyntheticEvent, value: string) => void;
  /** Render the input */
  renderInput: (params: AutocompleteRenderInputParams) => React.ReactNode;
  /** Render the option */
  renderOption?: (props: React.HTMLAttributes<HTMLLIElement>, option: T) => React.ReactNode;
  /** A filter function for options */
  filterOptions?: (options: T[], state: FilterOptionsState<T>) => T[];
  /** Used to determine the string value for an option */
  getOptionLabel?: (option: T) => string;
  /** If true, handles multiple values */
  multiple?: boolean;
  /** If true, user can add arbitrary values */
  freeSolo?: boolean;
  /** If true, the component is in loading state */
  loading?: boolean;
  /** Text to display when loading */
  loadingText?: React.ReactNode;
  /** Text to display when no options */
  noOptionsText?: React.ReactNode;
  /** If true, the component is disabled */
  disabled?: boolean;
}
```

**Usage Examples:**

```typescript
import { Autocomplete, TextField } from "@mui/material";

const countries = [
  { code: 'US', label: 'United States' },
  { code: 'CA', label: 'Canada' },
  { code: 'UK', label: 'United Kingdom' },
];

// Basic autocomplete
<Autocomplete
  options={countries}
  getOptionLabel={(option) => option.label}
  renderInput={(params) => (
    <TextField {...params} label="Country" variant="outlined" />
  )}
  onChange={(_, value) => setSelectedCountry(value)}
/>

// Multiple selection
<Autocomplete
  multiple
  options={skills}
  getOptionLabel={(option) => option.name}
  renderInput={(params) => (
    <TextField {...params} label="Skills" placeholder="Select skills" />
  )}
  onChange={(_, value) => setSelectedSkills(value)}
/>
```

### Rating

Star rating input component for collecting user ratings.

```typescript { .api }
/**
 * Star rating input for collecting user ratings
 * @param props - Rating configuration
 * @returns Rating component
 */
function Rating(props: RatingProps): JSX.Element;

interface RatingProps extends CommonProps {
  /** The default value. Use when the component is not controlled */
  defaultValue?: number;
  /** If true, the component is disabled */
  disabled?: boolean;
  /** The icon to display when empty */
  emptyIcon?: React.ReactNode;
  /** Accepts a function which returns a string value for the rating label */
  getLabelText?: (value: number) => string;
  /** If true, only the selected icon will be highlighted */
  highlightSelectedOnly?: boolean;
  /** The icon to display */
  icon?: React.ReactNode;
  /** Maximum rating */
  max?: number;
  /** The name attribute of the radio inputs */
  name?: string;
  /** Callback fired when the value changes */
  onChange?: (event: React.SyntheticEvent, value: number | null) => void;
  /** Callback fired when the hover state changes */
  onChangeActive?: (event: React.SyntheticEvent, value: number) => void;
  /** The minimum increment value change allowed */
  precision?: number;
  /** Removes all hover effects and pointer events */
  readOnly?: boolean;
  /** The size of the component */
  size?: 'small' | 'medium' | 'large';
  /** The rating value */
  value?: number | null;
}
```

**Usage Examples:**

```typescript
import { Rating, Typography, Box } from "@mui/material";
import StarIcon from "@mui/icons-material/Star";

// Basic rating
<Rating name="simple-controlled" value={value} onChange={(_, newValue) => setValue(newValue)} />

// Read-only rating
<Rating name="read-only" value={4.5} readOnly />

// Custom icon rating
<Rating
  name="customized-empty"
  defaultValue={2}
  precision={0.5}
  emptyIcon={<StarIcon style={{ opacity: 0.55 }} fontSize="inherit" />}
/>

// Rating with label
<Box component="fieldset" mb={3} borderColor="transparent">
  <Typography component="legend">Overall rating</Typography>
  <Rating
    name="overall-rating"
    value={rating}
    onChange={(_, newValue) => setRating(newValue)}
    getLabelText={(value) => `${value} Star${value !== 1 ? 's' : ''}`}
  />
</Box>
```

### ToggleButton

Toggle button components for selecting between mutually exclusive options.

```typescript { .api }
/**
 * Toggle button for binary selection
 * @param props - ToggleButton configuration
 * @returns ToggleButton component
 */
function ToggleButton(props: ToggleButtonProps): JSX.Element;

/**
 * Group of toggle buttons for exclusive selection
 * @param props - ToggleButtonGroup configuration
 * @returns ToggleButtonGroup component
 */
function ToggleButtonGroup(props: ToggleButtonGroupProps): JSX.Element;

interface ToggleButtonProps extends CommonProps {
  /** The color of the button when it is selected */
  color?: 'standard' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, the component is selected */
  selected?: boolean;
  /** The size of the component */
  size?: 'small' | 'medium' | 'large';
  /** The value to associate with the button when selected */
  value: NonNullable<string | number>;
  children?: React.ReactNode;
}

interface ToggleButtonGroupProps extends CommonProps {
  /** The color of the button when it is selected */
  color?: 'standard' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** If true, only allow one of the child ToggleButton values to be selected */
  exclusive?: boolean;
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, the button group will take up the full width of its container */
  fullWidth?: boolean;
  /** Callback fired when the value changes */
  onChange?: (event: React.MouseEvent<HTMLElement>, value: any) => void;
  /** The component orientation */
  orientation?: 'horizontal' | 'vertical';
  /** The size of the component */
  size?: 'small' | 'medium' | 'large';
  /** The currently selected value within the group or an array of selected values */
  value?: any;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import FormatBoldIcon from "@mui/icons-material/FormatBold";
import FormatItalicIcon from "@mui/icons-material/FormatItalic";
import FormatUnderlinedIcon from "@mui/icons-material/FormatUnderlined";

// Exclusive selection
const [alignment, setAlignment] = React.useState('left');

<ToggleButtonGroup
  value={alignment}
  exclusive
  onChange={(_, newAlignment) => setAlignment(newAlignment)}
>
  <ToggleButton value="left">Left</ToggleButton>
  <ToggleButton value="center">Center</ToggleButton>
  <ToggleButton value="right">Right</ToggleButton>
</ToggleButtonGroup>

// Multiple selection
const [formats, setFormats] = React.useState(['bold']);

<ToggleButtonGroup
  value={formats}
  onChange={(_, newFormats) => setFormats(newFormats)}
>
  <ToggleButton value="bold">
    <FormatBoldIcon />
  </ToggleButton>
  <ToggleButton value="italic">
    <FormatItalicIcon />
  </ToggleButton>
  <ToggleButton value="underlined">
    <FormatUnderlinedIcon />
  </ToggleButton>
</ToggleButtonGroup>
```

### IconButton

Button component for displaying icons with interaction capabilities.

```typescript { .api }
/**
 * Button component for displaying icons with interaction capabilities
 * @param props - IconButton configuration
 * @returns IconButton component
 */
function IconButton(props: IconButtonProps): JSX.Element;

interface IconButtonProps extends CommonProps {
  /** The color of the component */
  color?: 'inherit' | 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, the keyboard focus ripple is disabled */
  disableFocusRipple?: boolean;
  /** Alignment adjustment for icon positioning */
  edge?: 'start' | 'end' | false;
  /** If true, the loading indicator is visible */
  loading?: boolean;
  /** Element to display when loading is true */
  loadingIndicator?: React.ReactNode;
  /** The size of the component */
  size?: 'small' | 'medium' | 'large';
  /** The icon element to display */
  children?: React.ReactNode;
  /** Callback fired when the button is clicked */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}
```

**Usage Examples:**

```typescript
import { IconButton } from "@mui/material";
import { Delete, Edit, Favorite } from "@mui/icons-material";

// Basic icon button
<IconButton color="primary">
  <Favorite />
</IconButton>

// Icon button with different sizes
<IconButton size="small">
  <Edit />
</IconButton>

// Disabled icon button
<IconButton disabled>
  <Delete />
</IconButton>

// Icon button with edge alignment
<IconButton edge="end" color="error">
  <Delete />
</IconButton>
```

### Fab (Floating Action Button)

Floating action button for primary actions that float above content.

```typescript { .api }
/**
 * Floating action button for primary actions that float above content
 * @param props - Fab configuration
 * @returns Fab component
 */
function Fab(props: FabProps): JSX.Element;

interface FabProps extends CommonProps {
  /** The color of the component */
  color?: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, the keyboard focus ripple is disabled */
  disableFocusRipple?: boolean;
  /** If true, the ripple effect is disabled */
  disableRipple?: boolean;
  /** The URL to link to when clicked */
  href?: string;
  /** The size of the component */
  size?: 'small' | 'medium' | 'large';
  /** The variant to use */
  variant?: 'circular' | 'extended';
  /** The content of the component */
  children?: React.ReactNode;
  /** Callback fired when clicked */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}
```

**Usage Examples:**

```typescript
import { Fab } from "@mui/material";
import { Add, Edit, Navigation } from "@mui/icons-material";

// Basic floating action button
<Fab color="primary">
  <Add />
</Fab>

// Extended FAB with text
<Fab variant="extended" color="secondary">
  <Navigation sx={{ mr: 1 }} />
  Navigate
</Fab>

// Small FAB
<Fab size="small" color="error">
  <Edit />
</Fab>

// Disabled FAB
<Fab disabled>
  <Add />
</Fab>
```

### ButtonGroup

Component for grouping related buttons together.

```typescript { .api }
/**
 * Component for grouping related buttons together
 * @param props - ButtonGroup configuration
 * @returns ButtonGroup component
 */
function ButtonGroup(props: ButtonGroupProps): JSX.Element;

interface ButtonGroupProps extends CommonProps {
  /** The color of the component */
  color?: 'inherit' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, no elevation is used */
  disableElevation?: boolean;
  /** If true, the button ripple effect is disabled */
  disableRipple?: boolean;
  /** If true, the buttons take up the full width */
  fullWidth?: boolean;
  /** The group orientation */
  orientation?: 'horizontal' | 'vertical';
  /** The size of the component */
  size?: 'small' | 'medium' | 'large';
  /** The variant to use */
  variant?: 'text' | 'outlined' | 'contained';
  /** The content of the component */
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { ButtonGroup, Button } from "@mui/material";

// Basic button group
<ButtonGroup variant="contained">
  <Button>One</Button>
  <Button>Two</Button>
  <Button>Three</Button>
</ButtonGroup>

// Vertical button group
<ButtonGroup orientation="vertical" variant="outlined">
  <Button>Top</Button>
  <Button>Middle</Button>
  <Button>Bottom</Button>
</ButtonGroup>

// Full width button group
<ButtonGroup fullWidth variant="text">
  <Button>First</Button>
  <Button>Second</Button>
</ButtonGroup>
```

### ButtonBase

Foundation component for building custom button components.

```typescript { .api }
/**
 * Foundation component for building custom button components
 * @param props - ButtonBase configuration
 * @returns ButtonBase component
 */
function ButtonBase(props: ButtonBaseProps): JSX.Element;

interface ButtonBaseProps extends CommonProps {
  /** A ref for imperative actions */
  action?: React.Ref<ButtonBaseActions>;
  /** If true, the ripples are centered */
  centerRipple?: boolean;
  /** The content of the component */
  children?: React.ReactNode;
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, the keyboard focus ripple is disabled */
  disableFocusRipple?: boolean;
  /** If true, the ripple effect is disabled */
  disableRipple?: boolean;
  /** If true, the touch ripple effect is disabled */
  disableTouchRipple?: boolean;
  /** If true, the base will have a keyboard focus ripple */
  focusRipple?: boolean;
  /** The component used for the root node */
  component?: React.ElementType;
  /** Callback fired when clicked */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  /** Callback fired when focus is visible */
  onFocusVisible?: (event: React.FocusEvent<HTMLButtonElement>) => void;
}

interface ButtonBaseActions {
  focusVisible(): void;
}
```

**Usage Examples:**

```typescript
import { ButtonBase, Typography } from "@mui/material";

// Custom button using ButtonBase
<ButtonBase
  sx={{
    p: 2,
    border: '1px solid',
    borderColor: 'divider',
    borderRadius: 1,
    '&:hover': {
      backgroundColor: 'action.hover',
    },
  }}
>
  <Typography variant="body2">
    Custom Button
  </Typography>
</ButtonBase>

// ButtonBase as a link
<ButtonBase component="a" href="/profile" sx={{ p: 1 }}>
  Go to Profile
</ButtonBase>
```