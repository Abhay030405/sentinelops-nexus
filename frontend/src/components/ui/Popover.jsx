import React from 'react';
import * as PopoverPrimitive from '@radix-ui/react-popover';

const Popover = PopoverPrimitive.Root;

const PopoverTrigger = PopoverPrimitive.Trigger;

const PopoverContent = React.forwardRef(
  (
    {
      style,
      align = 'center',
      sideOffset = 4,
      ...props
    },
    ref
  ) => (
    <PopoverPrimitive.Portal>
      <PopoverPrimitive.Content
        ref={ref}
        align={align}
        sideOffset={sideOffset}
        style={{
          zIndex: 50,
          width: '288px',
          borderRadius: '0.5rem',
          border: '1px solid var(--border-color)',
          backgroundColor: 'var(--bg-secondary)',
          padding: '1rem',
          color: 'var(--text-primary)',
          boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.3)',
          outline: 'none',
          animation: 'fadeIn 0.2s ease-out',
          ...style,
        }}
        {...props}
      />
    </PopoverPrimitive.Portal>
  )
);

PopoverContent.displayName = PopoverPrimitive.Content.displayName;

export { Popover, PopoverTrigger, PopoverContent };
