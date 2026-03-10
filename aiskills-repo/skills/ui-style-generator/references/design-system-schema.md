# DesignSystem Schema

Full JSON schema to generate. All fields are required unless marked optional.

```typescript
interface ColorScheme {
  primary: string;           // Main brand color (hex)
  primaryHover: string;      // Darker/lighter version for hover (hex)
  secondary: string;         // Accent color (hex)
  surface: string;           // Card/container background (hex)
  surfaceHighlight: string;  // Hover/active surface state (hex)
  background: string;        // App background (hex)
  text: string;              // Main text color (hex)
  textSecondary: string;     // Subtext/muted color (hex)
  border: string;            // Border color (hex)
  success: string;           // Success state (hex)
  warning: string;           // Warning state (hex)
  error: string;             // Error state (hex)
}

interface DesignSystem {
  projectName: string;       // Creative project name
  description: string;       // Short professional style description

  colors: {
    light: ColorScheme;
    dark: ColorScheme;
  };

  gradients: {
    primary: string;         // CSS linear-gradient() matching primary
    secondary: string;       // CSS linear-gradient() matching secondary
  };

  typography: {
    fontFamily: string;      // Google Font name (e.g. "Inter", "Poppins")
    scale: {
      h1: string;            // e.g. "48px"
      h2: string;            // e.g. "36px"
      h3: string;            // e.g. "24px"
      body: string;          // e.g. "16px"
      caption: string;       // e.g. "12px"
    };
  };

  spacing: {
    base: number;            // Base unit (e.g. 4)
    scale: {
      xs: string;            // e.g. "4px"
      sm: string;            // e.g. "8px"
      md: string;            // e.g. "16px"
      lg: string;            // e.g. "24px"
      xl: string;            // e.g. "40px"
      xxl: string;           // e.g. "64px"
    };
  };

  animation: {
    easing: string;          // CSS easing (e.g. "cubic-bezier(0.4, 0, 0.2, 1)")
    duration: {
      fast: string;          // e.g. "150ms"
      normal: string;        // e.g. "300ms"
      slow: string;          // e.g. "500ms"
    };
  };

  layout: {
    containerWidth: string;  // e.g. "1280px"
    gridColumns: number;     // e.g. 12
    gridGap: string;         // e.g. "24px"
  };

  effects: {
    glass: string;           // backdrop-filter value e.g. "blur(10px)"
    borderWidth: string;     // e.g. "1px"
  };

  iconStyle: string;         // e.g. "Outlined", "Filled", "Duotone"

  borderRadius: {
    small: string;           // e.g. "4px"
    medium: string;          // e.g. "8px"
    large: string;           // e.g. "16px"
    full: string;            // "9999px"
  };

  shadows: {
    sm: string;              // CSS box-shadow small elevation
    md: string;              // CSS box-shadow medium elevation
    lg: string;              // CSS box-shadow large elevation
  };
}
```

## Example Output (fintech dashboard, dark minimal)

```json
{
  "projectName": "NexusFinance",
  "description": "Dark, minimal fintech dashboard with sharp edges and high-contrast data visualization",
  "colors": {
    "light": {
      "primary": "#2563EB",
      "primaryHover": "#1D4ED8",
      "secondary": "#10B981",
      "surface": "#F8FAFC",
      "surfaceHighlight": "#F1F5F9",
      "background": "#FFFFFF",
      "text": "#0F172A",
      "textSecondary": "#64748B",
      "border": "#E2E8F0",
      "success": "#10B981",
      "warning": "#F59E0B",
      "error": "#EF4444"
    },
    "dark": {
      "primary": "#3B82F6",
      "primaryHover": "#60A5FA",
      "secondary": "#34D399",
      "surface": "#1E293B",
      "surfaceHighlight": "#334155",
      "background": "#0F172A",
      "text": "#F8FAFC",
      "textSecondary": "#94A3B8",
      "border": "#334155",
      "success": "#34D399",
      "warning": "#FBBF24",
      "error": "#F87171"
    }
  },
  "gradients": {
    "primary": "linear-gradient(135deg, #2563EB 0%, #7C3AED 100%)",
    "secondary": "linear-gradient(135deg, #10B981 0%, #06B6D4 100%)"
  },
  "typography": {
    "fontFamily": "Inter",
    "scale": { "h1": "48px", "h2": "36px", "h3": "24px", "body": "16px", "caption": "12px" }
  },
  "spacing": {
    "base": 4,
    "scale": { "xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "40px", "xxl": "64px" }
  },
  "animation": {
    "easing": "cubic-bezier(0.4, 0, 0.2, 1)",
    "duration": { "fast": "150ms", "normal": "300ms", "slow": "500ms" }
  },
  "layout": { "containerWidth": "1280px", "gridColumns": 12, "gridGap": "24px" },
  "effects": { "glass": "blur(12px)", "borderWidth": "1px" },
  "iconStyle": "Outlined",
  "borderRadius": { "small": "4px", "medium": "8px", "large": "16px", "full": "9999px" },
  "shadows": {
    "sm": "0 1px 3px rgba(0,0,0,0.3)",
    "md": "0 4px 16px rgba(0,0,0,0.4)",
    "lg": "0 8px 32px rgba(0,0,0,0.5)"
  }
}
```
