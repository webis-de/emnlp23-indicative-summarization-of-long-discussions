import { Switch } from "@headlessui/react";

function Toggle({ checked, onChange, onBlur }) {
  return (
    <Switch
      checked={checked}
      onChange={onChange}
      onBlur={onBlur}
      className={`${
        checked ? "bg-blue-600" : "bg-gray-400"
      } border-transparent focus-visible:ring-white relative inline-flex h-[24px] w-[46px] flex-shrink-0 cursor-pointer rounded-full border-2 transition-colors duration-200 ease-in-out focus:outline-none  focus-visible:ring-2 focus-visible:ring-opacity-75`}
    >
      <span
        aria-hidden="true"
        className={`${
          checked ? "translate-x-[22px]" : ""
        } bg-white pointer-events-none inline-block h-[20px] w-[20px] transform rounded-full shadow-lg ring-0 transition duration-200 ease-in-out`}
      />
    </Switch>
  );
}

export { Toggle };
