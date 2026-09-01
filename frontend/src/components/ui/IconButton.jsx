import React from 'react';

const IconButton = React.forwardRef(({
  icon: Icon,
  onClick,
  className = '',
  ariaLabel,
  title,
  variant = 'primary',
  size = 'md',
  disabled = false,
  badge,
  ...props
}, ref) => {
  const baseStyles = 'inline-flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none relative';

  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500 active:bg-primary-800',
    secondary: 'bg-secondary-700 text-white hover:bg-secondary-800 focus:ring-secondary-500 active:bg-secondary-900',
    outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 focus:ring-primary-500 active:bg-primary-100',
    ghost: 'text-primary-600 hover:bg-primary-50 focus:ring-primary-500 active:bg-primary-100',
    danger: 'bg-danger-600 text-white hover:bg-danger-700 focus:ring-danger-500 active:bg-danger-800',
    success: 'bg-success-600 text-white hover:bg-success-700 focus:ring-success-500 active:bg-success-800',
  };

  const sizes = {
    sm: 'w-8 h-8 rounded-lg',
    md: 'w-10 h-10 rounded-lg',
    lg: 'w-12 h-12 rounded-xl',
  };

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  const combinedClassName = `${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`;

  return (
    <button
      ref={ref}
      onClick={onClick}
      disabled={disabled}
      aria-label={ariaLabel}
      title={title}
      className={combinedClassName}
      {...props}
    >
      <Icon className={iconSizes[size]} />
      {badge && (
        <span className="absolute -top-1 -right-1 bg-danger-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center shadow-md">
          {badge}
        </span>
      )}
    </button>
  );
});

IconButton.displayName = 'IconButton';

export default IconButton;
