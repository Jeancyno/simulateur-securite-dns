import React from 'react';

const Button = React.forwardRef(({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
  ariaLabel,
  title,
  type = 'button',
  fullWidth = false,
  icon: Icon,
  iconPosition = 'left',
  ...props
}, ref) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none';

  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500 active:bg-primary-800',
    secondary: 'bg-secondary-700 text-white hover:bg-secondary-800 focus:ring-secondary-500 active:bg-secondary-900',
    outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 focus:ring-primary-500 active:bg-primary-100',
    ghost: 'text-primary-600 hover:bg-primary-50 focus:ring-primary-500 active:bg-primary-100',
    danger: 'bg-danger-600 text-white hover:bg-danger-700 focus:ring-danger-500 active:bg-danger-800',
    success: 'bg-success-600 text-white hover:bg-success-700 focus:ring-success-500 active:bg-success-800',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm rounded-lg gap-1.5',
    md: 'px-4 py-2 text-base rounded-lg gap-2',
    lg: 'px-6 py-3 text-lg rounded-xl gap-2.5',
  };

  const responsiveSizes = {
    sm: 'px-3 py-1.5 text-sm sm:px-4 sm:py-2 sm:text-base rounded-lg gap-1.5 sm:gap-2',
    md: 'px-4 py-2 text-sm sm:text-base rounded-lg gap-2',
    lg: 'px-5 py-2.5 text-base sm:text-lg sm:px-6 sm:py-3 rounded-lg sm:rounded-xl gap-2 sm:gap-2.5',
  };

  const widthClass = fullWidth ? 'w-full' : '';

  const combinedClassName = `${baseStyles} ${variants[variant]} ${responsiveSizes[size]} ${widthClass} ${className}`;

  return (
    <button
      ref={ref}
      type={type}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      title={title}
      className={combinedClassName}
      {...props}
    >
      {Icon && iconPosition === 'left' && <Icon className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" />}
      {children}
      {Icon && iconPosition === 'right' && <Icon className="w-4 h-4 sm:w-5 sm:h-5 flex-shrink-0" />}
    </button>
  );
});

Button.displayName = 'Button';

export default Button;
