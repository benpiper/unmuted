# Form Components

Complete form controls including text fields, selects, checkboxes, and form validation with Material Design styling.

## Capabilities

### TextField

Complete text field component with label, input, helper text, and error states.

```typescript { .api }
/**
 * Complete text field with label, input and helper text
 * @param props - TextField configuration
 * @returns TextField component
 */
function TextField(props: TextFieldProps): JSX.Element;

interface TextFieldProps extends CommonProps {
  /** The variant to use */
  variant?: 'filled' | 'outlined' | 'standard';
  /** The size of the component */
  size?: 'small' | 'medium';
  /** The color of the component */
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** If true, the component takes up the full width of its container */
  fullWidth?: boolean;
  /** The label content */
  label?: React.ReactNode;
  /** The helper text content */
  helperText?: React.ReactNode;
  /** If true, the label is displayed in an error state */
  error?: boolean;
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, the Input will be required */
  required?: boolean;
  /** The default value */
  defaultValue?: unknown;
  /** The value of the component */
  value?: unknown;
  /** Callback fired when the value is changed */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  /** Name attribute of the input element */
  name?: string;
  /** The short hint displayed in the input before the user enters a value */
  placeholder?: string;
  /** Type of the input element */
  type?: string;
  /** If true, the component will be displayed in focused state */
  autoFocus?: boolean;
  /** If true, the component displays a multiline input */
  multiline?: boolean;
  /** Maximum number of rows to display when multiline option is set to true */
  maxRows?: number;
  /** Minimum number of rows to display when multiline option is set to true */
  minRows?: number;
  /** Number of rows to display when multiline option is set to true */
  rows?: number;
  /** Render a Select element while passing the Input element to Select as input parameter */
  select?: boolean;
  /** The option elements to populate the select with */
  children?: React.ReactNode;
  /** Props applied to the Input element */
  InputProps?: Partial<OutlinedInputProps>;
  /** Props applied to the InputLabel element */
  InputLabelProps?: Partial<InputLabelProps>;
  /** Props applied to the FormHelperText element */
  FormHelperTextProps?: Partial<FormHelperTextProps>;
}
```

**Usage Examples:**

```typescript
import { TextField, MenuItem } from "@mui/material";

// Basic text field
<TextField
  label="Email"
  variant="outlined"
  type="email"
  fullWidth
  required
/>

// Text field with helper text and error
<TextField
  label="Password"
  type="password"
  error
  helperText="Password must be at least 8 characters"
  fullWidth
/>

// Multiline text field
<TextField
  label="Description"
  multiline
  rows={4}
  fullWidth
  placeholder="Enter your description here..."
/>

// Select field
<TextField
  select
  label="Country"
  value={country}
  onChange={handleChange}
  fullWidth
>
  <MenuItem value="us">United States</MenuItem>
  <MenuItem value="ca">Canada</MenuItem>
  <MenuItem value="uk">United Kingdom</MenuItem>
</TextField>
```

### FormControl

Provides context such as filled/focused/error/required for form inputs.

```typescript { .api }
/**
 * Form control wrapper providing context
 * @param props - FormControl configuration
 * @returns FormControl component
 */
function FormControl(props: FormControlProps): JSX.Element;

interface FormControlProps extends CommonProps {
  /** The color of the component */
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, the label should be displayed in an error state */
  error?: boolean;
  /** If true, the component will take up the full width of its container */
  fullWidth?: boolean;
  /** If true, the component is focused */
  focused?: boolean;
  /** If true, the label is hidden */
  hiddenLabel?: boolean;
  /** The margin to apply to the component */
  margin?: 'dense' | 'normal' | 'none';
  /** If true, the label will indicate that the input is required */
  required?: boolean;
  /** The size of the component */
  size?: 'small' | 'medium';
  /** The variant to use */
  variant?: 'standard' | 'outlined' | 'filled';
  /** The component used for the root node */
  component?: React.ElementType;
  children?: React.ReactNode;
}
```

### FormControlLabel

Drop-in replacement for labels with built-in FormControl context.

```typescript { .api }
/**
 * Label with FormControl context
 * @param props - FormControlLabel configuration
 * @returns FormControlLabel component
 */
function FormControlLabel(props: FormControlLabelProps): JSX.Element;

interface FormControlLabelProps extends CommonProps {
  /** A control element. For instance, it can be a Radio, a Switch or a Checkbox */
  control: React.ReactElement;
  /** The text to be used in an enclosing label element */
  label: React.ReactNode;
  /** The position of the label */
  labelPlacement?: 'end' | 'start' | 'top' | 'bottom';
  /** If true, the component appears selected */
  checked?: boolean;
  /** If true, the control is disabled */
  disabled?: boolean;
  /** Name attribute of the input element */
  name?: string;
  /** Callback fired when the state is changed */
  onChange?: (event: React.SyntheticEvent, checked: boolean) => void;
  /** The value of the component */
  value?: unknown;
  /** If true, the input element is required */
  required?: boolean;
}
```

### Checkbox

Checkbox input component with customizable states and styling.

```typescript { .api }
/**
 * Checkbox input component
 * @param props - Checkbox configuration
 * @returns Checkbox component
 */
function Checkbox(props: CheckboxProps): JSX.Element;

interface CheckboxProps extends CommonProps {
  /** If true, the component is checked */
  checked?: boolean;
  /** The icon to display when the component is checked */
  checkedIcon?: React.ReactNode;
  /** The color of the component */
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' | 'default';
  /** The default checked state */
  defaultChecked?: boolean;
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, the ripple effect is disabled */
  disableRipple?: boolean;
  /** The icon to display when the component is unchecked */
  icon?: React.ReactNode;
  /** If true, the component appears indeterminate */
  indeterminate?: boolean;
  /** The icon to display when the component is indeterminate */
  indeterminateIcon?: React.ReactNode;
  /** Attributes applied to the input element */
  inputProps?: React.InputHTMLAttributes<HTMLInputElement>;
  /** Pass a ref to the input element */
  inputRef?: React.Ref<HTMLInputElement>;
  /** Callback fired when the state is changed */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>, checked: boolean) => void;
  /** If true, the input element is required */
  required?: boolean;
  /** The size of the component */
  size?: 'small' | 'medium';
  /** The value of the component */
  value?: unknown;
}
```

**Usage Examples:**

```typescript
import { Checkbox, FormControlLabel, FormGroup } from "@mui/material";

// Basic checkbox
<FormControlLabel
  control={<Checkbox />}
  label="Accept terms and conditions"
/>

// Controlled checkbox
<FormControlLabel
  control={
    <Checkbox
      checked={checked}
      onChange={handleChange}
      color="primary"
    />
  }
  label="Enable notifications"
/>

// Checkbox group
<FormGroup>
  <FormControlLabel control={<Checkbox />} label="Option 1" />
  <FormControlLabel control={<Checkbox />} label="Option 2" />
  <FormControlLabel control={<Checkbox />} label="Option 3" />
</FormGroup>
```

### Radio and RadioGroup

Radio button components for single selection from multiple options.

```typescript { .api }
/**
 * Radio button input component
 * @param props - Radio configuration
 * @returns Radio component
 */
function Radio(props: RadioProps): JSX.Element;

/**
 * Groups radio buttons and manages selection
 * @param props - RadioGroup configuration
 * @returns RadioGroup component
 */
function RadioGroup(props: RadioGroupProps): JSX.Element;

interface RadioProps extends CommonProps {
  /** If true, the component is checked */
  checked?: boolean;
  /** The icon to display when the component is checked */
  checkedIcon?: React.ReactNode;
  /** The color of the component */
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' | 'default';
  /** If true, the component is disabled */
  disabled?: boolean;
  /** If true, the ripple effect is disabled */
  disableRipple?: boolean;
  /** The icon to display when the component is unchecked */
  icon?: React.ReactNode;
  /** Attributes applied to the input element */
  inputProps?: React.InputHTMLAttributes<HTMLInputElement>;
  /** Name attribute of the input element */
  name?: string;
  /** Callback fired when the state is changed */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  /** If true, the input element is required */
  required?: boolean;
  /** The size of the component */
  size?: 'small' | 'medium';
  /** The value of the component */
  value?: unknown;
}

interface RadioGroupProps extends CommonProps {
  /** The default selected value */
  defaultValue?: unknown;
  /** The name used to reference the value of the control */
  name?: string;
  /** Callback fired when a radio button is selected */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>, value: string) => void;
  /** Display group of radio buttons in a row */
  row?: boolean;
  /** Value of the selected radio button */
  value?: unknown;
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Radio, RadioGroup, FormControlLabel, FormControl, FormLabel } from "@mui/material";

// Radio group
<FormControl component="fieldset">
  <FormLabel component="legend">Gender</FormLabel>
  <RadioGroup
    aria-label="gender"
    name="gender"
    value={value}
    onChange={handleChange}
  >
    <FormControlLabel value="female" control={<Radio />} label="Female" />
    <FormControlLabel value="male" control={<Radio />} label="Male" />
    <FormControlLabel value="other" control={<Radio />} label="Other" />
  </RadioGroup>
</FormControl>
```

### Select

Select dropdown component for choosing from multiple options.

```typescript { .api }
/**
 * Select dropdown component
 * @param props - Select configuration
 * @returns Select component
 */
function Select<T>(props: SelectProps<T>): JSX.Element;

interface SelectProps<T> extends CommonProps {
  /** If true, the width of the popover will automatically be set according to the items inside the menu */
  autoWidth?: boolean;
  /** The default selected value */
  defaultValue?: T;
  /** If true, a value is displayed even if no items are selected */
  displayEmpty?: boolean;
  /** The icon that displays the arrow */
  IconComponent?: React.ComponentType;
  /** The input component */
  input?: React.ReactElement;
  /** Attributes applied to the input element */
  inputProps?: React.InputHTMLAttributes<HTMLInputElement>;
  /** The label element */
  label?: React.ReactNode;
  /** The ID of an element that acts as an additional label */
  labelId?: string;
  /** Props applied to the Menu element */
  MenuProps?: Partial<MenuProps>;
  /** If true, value must be an array and the menu will support multiple selections */
  multiple?: boolean;
  /** If true, the component uses a native select element */
  native?: boolean;
  /** Callback fired when a menu item is selected */
  onChange?: (event: SelectChangeEvent<T>, child: React.ReactNode) => void;
  /** Callback fired when the component requests to be closed */
  onClose?: (event: React.SyntheticEvent) => void;
  /** Callback fired when the component requests to be opened */
  onOpen?: (event: React.SyntheticEvent) => void;
  /** If true, the component is shown */
  open?: boolean;
  /** Render the selected value */
  renderValue?: (value: T) => React.ReactNode;
  /** Props applied to the clickable div element */
  SelectDisplayProps?: React.HTMLAttributes<HTMLDivElement>;
  /** The input value */
  value?: T;
  /** The variant to use */
  variant?: 'standard' | 'outlined' | 'filled';
  children?: React.ReactNode;
}
```

**Usage Examples:**

```typescript
import { Select, MenuItem, FormControl, InputLabel } from "@mui/material";

// Basic select
<FormControl fullWidth>
  <InputLabel>Age</InputLabel>
  <Select
    value={age}
    label="Age"
    onChange={handleChange}
  >
    <MenuItem value={10}>Ten</MenuItem>
    <MenuItem value={20}>Twenty</MenuItem>
    <MenuItem value={30}>Thirty</MenuItem>
  </Select>
</FormControl>

// Multiple select
<Select
  multiple
  value={selectedItems}
  onChange={handleChange}
  renderValue={(selected) => selected.join(', ')}
>
  <MenuItem value="option1">Option 1</MenuItem>
  <MenuItem value="option2">Option 2</MenuItem>
  <MenuItem value="option3">Option 3</MenuItem>
</Select>
```

## Form Validation Pattern

```typescript
import React, { useState } from "react";
import {
  TextField,
  Button,
  FormControl,
  FormHelperText,
  Box
} from "@mui/material";

interface FormData {
  email: string;
  password: string;
  confirmPassword: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
}

function SignupForm() {
  const [formData, setFormData] = useState<FormData>({
    email: "",
    password: "",
    confirmPassword: ""
  });
  const [errors, setErrors] = useState<FormErrors>({});

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    if (!formData.email.includes("@")) {
      newErrors.email = "Please enter a valid email address";
    }
    
    if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (validateForm()) {
      // Submit form
      console.log("Form submitted:", formData);
    }
  };

  const handleChange = (field: keyof FormData) => 
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setFormData(prev => ({
        ...prev,
        [field]: event.target.value
      }));
      // Clear error when user starts typing
      if (errors[field]) {
        setErrors(prev => ({
          ...prev,
          [field]: undefined
        }));
      }
    };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
      <TextField
        margin="normal"
        required
        fullWidth
        label="Email Address"
        type="email"
        value={formData.email}
        onChange={handleChange('email')}
        error={!!errors.email}
        helperText={errors.email}
      />
      
      <TextField
        margin="normal"
        required
        fullWidth
        label="Password"
        type="password"
        value={formData.password}
        onChange={handleChange('password')}
        error={!!errors.password}
        helperText={errors.password}
      />
      
      <TextField
        margin="normal"
        required
        fullWidth
        label="Confirm Password"
        type="password"
        value={formData.confirmPassword}
        onChange={handleChange('confirmPassword')}
        error={!!errors.confirmPassword}
        helperText={errors.confirmPassword}
      />
      
      <Button
        type="submit"
        fullWidth
        variant="contained"
        sx={{ mt: 3, mb: 2 }}
      >
        Sign Up
      </Button>
    </Box>
  );
}
```