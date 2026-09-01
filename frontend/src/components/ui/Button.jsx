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
  // Styles de base
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  // Variantes avec des couleurs standard
  const variantStyles = {
    primary: 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500 text-white',
    secondary: 'bg-gray-700 hover:bg-gray-800 focus:ring-gray-500 text-white',
    outline: 'border-2 border-blue-600 hover:bg-blue-50 focus:ring-blue-500 text-blue-600',
    ghost: 'hover:bg-blue-50 focus:ring-blue-500 text-blue-600',
    danger: 'bg-red-600 hover:bg-red-700 focus:ring-red-500 text-white',
    success: 'bg-emerald-600 hover:bg-emerald-700 focus:ring-emerald-500 text-white',
  };
  
  // Tailles
  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm rounded-lg',
    md: 'px-4 py-2 text-base rounded-lg',
    lg: 'px-6 py-3 text-lg rounded-xl',
  };
  
  const widthClass = fullWidth ? 'w-full' : '';
  
  const combinedClassName = [
    baseStyles,
    variantStyles[variant] || variantStyles.primary,
    sizeStyles[size] || sizeStyles.md,
    widthClass,
    className
  ].filter(Boolean).join(' ');
  
  // Rendu de l'icône
  const renderIcon = () => {
    if (!Icon) return null;
    return (
      <span className="flex-shrink-0 inline-block">
        <Icon className="w-4 h-4 sm:w-5 sm:h-5" />
      </span>
    );
  };
  
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
      {iconPosition === 'left' && renderIcon()}
      <span className="inline-block">{children}</span>
      {iconPosition === 'right' && renderIcon()}
    </button>
  );
});

Button.displayName = 'Button';

export default Button;