import { Dialog } from "@headlessui/react";
import React, { useState } from "react";

function ModalTitle({ children }) {
  return (
    <Dialog.Title className="whitespace-nowrap text-3xl font-bold">
      {children}
    </Dialog.Title>
  );
}

const useModal = () => {
  const [isOpen, setIsOpen] = useState(false);
  const open = () => setIsOpen(true);
  const close = () => setIsOpen(false);
  return [isOpen, open, close];
};

function Modal({ children, isOpen, close, fit, level = 1 }) {
  let fitClass = "";
  let style = {};
  if (fit) {
    fitClass = "top-1/2 left-1/2 transform -translate-x-1/2 -translate-x-1/2";
  } else {
    style = { inset: `${1.5 * level}rem ${2 * level}rem` };
  }
  return (
    <Dialog open={isOpen} onClose={close}>
      <Dialog.Overlay className="fixed inset-0 z-20 bg-black opacity-30" />
      <div
        style={style}
        className={`${fitClass} bg-slate fixed z-50 flex overflow-y-auto border bg-white shadow-xl shadow-stone-400`}
      >
        {children}
      </div>
    </Dialog>
  );
}

export { Modal, ModalTitle, useModal };
