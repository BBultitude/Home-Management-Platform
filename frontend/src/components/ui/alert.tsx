import * as React from "react"

const alertVariants = {
  default: "bg-background text-foreground border-gray-200",
  destructive: "bg-red-50 border-red-300 text-red-800",
}

export interface AlertProps
  extends React.HTMLAttributes<HTMLDivElement> {
  variant?: keyof typeof alertVariants
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = "default", ...props }, ref) => (
    <div
      ref={ref}
      role="alert"
      className={`relative w-full rounded-lg border p-4 ${alertVariants[variant]} ${className || ''}`}
      {...props}
    />
  )
)
Alert.displayName = "Alert"

const AlertDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={`text-sm font-medium [&_p]:leading-relaxed ${className || ''}`}
      {...props}
    />
))
AlertDescription.displayName = "AlertDescription"

export { Alert, AlertDescription }
