import React, { useCallback, useState } from "react";

import { useLocalStorage } from "../hooks/local_storage";
import { defined } from "../util/common";

const SettingsContext = React.createContext();

function validateInt(value, { minValue = 256, maxValue = 2 ** 32 } = {}) {
  if (!defined(value)) return NaN;
  let number = value;
  if (!Number.isFinite(number)) {
    number = parseInt(number.toString().replace(/[^0-9-]/g, ""), 10);
  }
  if (minValue !== null) number = Math.max(number, minValue);
  if (maxValue !== null) number = Math.min(number, maxValue);
  return number;
}

function validateFloat(value, { minValue = 256, maxValue = 2 ** 32 } = {}) {
  if (!defined(value)) return NaN;
  let number = value;
  if (!Number.isFinite(number)) {
    number = parseFloat(number.toString().replace(/[^0-9-.]/g, ""));
  }
  if (minValue !== null) number = Math.max(number, minValue);
  if (maxValue !== null) number = Math.min(number, maxValue);
  return number;
}

function validateNumber(newValue, validateFunc, defaultValue) {
  let value = validateFunc(newValue);
  if (Number.isNaN(value)) {
    value = defaultValue;
  }
  return value;
}

function makeUseStored(validateFunc) {
  return (name, defaultValue) => {
    const [value, _setValue] = useLocalStorage(name, defaultValue);
    const setValue = useCallback(
      (newValue) => {
        _setValue(validateFunc(newValue, defaultValue));
      },
      [defaultValue, _setValue]
    );
    return [value, setValue];
  };
}

const useString = makeUseStored(
  (newValue, defaultValue) => (newValue && newValue.trim()) || defaultValue
);
const useInt = makeUseStored((newValue, defaultValue) =>
  validateNumber(newValue, validateInt, defaultValue)
);
const useProbability = makeUseStored((newValue, defaultValue) =>
  validateNumber(
    newValue,
    (e) => validateFloat(e, { minValue: 0, maxValue: 1 }),
    defaultValue
  )
);
const useTemperature = makeUseStored((newValue, defaultValue) =>
  validateNumber(
    newValue,
    (e) => validateFloat(e, { minValue: 0, maxValue: 2 }),
    defaultValue
  )
);

const _labelInstruction =
  "Every input is the content of a debate. For every input, you generate a single descriptive phrase that describes that input in very simple language, without talking about the debate or the author.";
const _frameInstruction = `The following list contains all available media frames as defined in the work from Boydstun, Amber E. et al. "Tracking the Development of Media Frames within and across Policy Issues." (2014): ["economic", "capacity and resources", "morality", "fairness and equality", "legality, constitutionality and jurisprudence", "policy prescription and evaluation", "crime and punishment", "security and defense", "health and safety", "quality of life", "cultural identity", "public opinion", "political", "external regulation and reputation"]
For every input, you answer with three of these media frames corresponding to that input, in order of importance.`;

const DEFAULTS = {
  labelInstruction: _labelInstruction,
  frameInstruction: _frameInstruction,
  coloredText: false,
  computeLabels: false,
  visualizeClusters: false,
  maxTokensPerCluster: null,
  apiKey: null,
  model: null,
  topP: 0.5,
  temperature: 0.0,
  showMinimap: true,
};

function SettingsProvider({ children }) {
  const [computeLabels, setComputeLabels] = useState(DEFAULTS.computeLabels);
  const [coloredText, setColoredText] = useLocalStorage(
    "colored-text",
    DEFAULTS.coloredText
  );
  const [visualizeClusters, setVisualizeClusters] = useLocalStorage(
    "visualize-clusters",
    DEFAULTS.visualizeClusters
  );
  const [apiKey, setApiKey] = useString("openai-api-key", DEFAULTS.apiKey);
  const [labelInstruction, setLabelInstruction] = useString(
    "labelInstruction",
    DEFAULTS.labelInstruction
  );
  const [frameInstruction, setFrameInstruction] = useString(
    "frameInstruction",
    DEFAULTS.frameInstruction
  );
  const [model, setModel] = useString("label-model", DEFAULTS.model);
  const [topP, setTopP] = useProbability("top-p", DEFAULTS.topP);
  const [temperature, setTemperature] = useTemperature(
    "temperature",
    DEFAULTS.temperature
  );
  const [maxTokensPerCluster, setMaxTokensPerCluster] = useInt(
    "max-tokens-per-cluster",
    DEFAULTS.maxTokensPerCluster
  );
  const [showMinimap, setShowMinimap] = useLocalStorage(
    "toggle-minimap",
    DEFAULTS.showMinimap
  );
  return (
    <SettingsContext.Provider
      value={{
        apiKey,
        computeLabels,
        coloredText,
        maxTokensPerCluster,
        model,
        labelInstruction,
        frameInstruction,
        setApiKey,
        setComputeLabels,
        setMaxTokensPerCluster,
        setModel,
        setLabelInstruction,
        setFrameInstruction,
        setShowMinimap,
        setColoredText,
        setVisualizeClusters,
        setTemperature,
        setTopP,
        showMinimap,
        visualizeClusters,
        temperature,
        topP,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}

export { SettingsContext, SettingsProvider, DEFAULTS };
