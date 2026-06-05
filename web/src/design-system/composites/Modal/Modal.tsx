import * as React from 'react';
import { cn } from '../../foundations/cn';
import styles from './modal.module.css';

export interface ModalProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({
  open = false,
  onOpenChange,
  children,
}) => {
  if (!open) return null;

  return (
    <div className={styles.root}>
      <div
        className={styles.overlay}
        onClick={() => onOpenChange?.(false)}
      />
      <div className={styles.content}>
        {children}
      </div>
    </div>
  );
};
Modal.displayName = 'Modal';

export interface ModalHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

export const ModalHeader: React.FC<ModalHeaderProps> = ({ className, ...props }) => {
  return <div className={cn(styles.header, className)} {...props} />;
};
ModalHeader.displayName = 'ModalHeader';

export interface ModalTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {}

export const ModalTitle: React.FC<ModalTitleProps> = ({ className, ...props }) => {
  return <h2 className={cn(styles.title, className)} {...props} />;
};
ModalTitle.displayName = 'ModalTitle';

export interface ModalDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {}

export const ModalDescription: React.FC<ModalDescriptionProps> = ({ className, ...props }) => {
  return <p className={cn(styles.description, className)} {...props} />;
};
ModalDescription.displayName = 'ModalDescription';

export interface ModalFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

export const ModalFooter: React.FC<ModalFooterProps> = ({ className, ...props }) => {
  return <div className={cn(styles.footer, className)} {...props} />;
};
ModalFooter.displayName = 'ModalFooter';

export interface ModalCloseProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

export const ModalClose: React.FC<ModalCloseProps> = ({ className, ...props }) => {
  return <button className={cn(styles.close, className)} {...props} />;
};
ModalClose.displayName = 'ModalClose';
