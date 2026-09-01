import React from 'react';

const Card = ({
  children,
  className = '',
  variant = 'default',
  padding = 'md',
  onClick,
  ...props
}) => {
  const baseStyles = 'rounded-xl transition-all duration-200';

  const variants = {
    default: 'bg-white border border-secondary-200 shadow-sm',
    elevated: 'bg-white border border-secondary-200 shadow-lg',
    gradient: 'bg-gradient-to-br from-primary-50 to-secondary-50 border border-primary-200 shadow-md',
    flat: 'bg-white border-0 shadow-none',
  };

  const paddings = {
    none: 'p-0',
    sm: 'p-3 sm:p-4',
    md: 'p-4 sm:p-6',
    lg: 'p-6 sm:p-8',
    xl: 'p-8 sm:p-10',
  };

  const hoverStyles = onClick
    ? 'cursor-pointer hover:shadow-lg hover:border-primary-300 active:scale-[0.99]'
    : '';

  const combinedClassName = `${baseStyles} ${variants[variant]} ${paddings[padding]} ${hoverStyles} ${className}`;

  const CardComponent = onClick ? 'button' : 'div';

  return (
    <CardComponent
      onClick={onClick}
      className={combinedClassName}
      {...props}
    >
      {children}
    </CardComponent>
  );
};

export default Card;
