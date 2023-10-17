import { useCallback, useContext, useMemo, useState } from "react";
import { FaCheckCircle, FaCog, FaExclamationCircle } from "react-icons/fa";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";

import { getThreadFromURL } from "../api";
import { DEFAULTS, SettingsContext } from "../context/settings";
import { useAsync } from "../hooks/async";
import { defined } from "../util/common";
import { Button } from "./Button";
import { Card, CardContent, CardHead } from "./Card";
import { Categories } from "./Categories";
import { Container } from "./Container";
import { GeneralError, SuccessFalseError } from "./Error";
import { Checkbox, Input, Textarea } from "./Form";
import { CenterLoading } from "./Loading";
import { Modal, ModalTitle, useModal } from "./Modal";
import { StoredList } from "./Stored";
import { HeadingMedium, HeadingSemiBig } from "./Text";
import { Thread } from "./Thread";
import { QuestionTooltip } from "./Tooltip";

function clipString(string, maxLength = 10) {
  let tmp = string.trimEnd();
  if (tmp.length > maxLength) {
    tmp = `${tmp.slice(0, maxLength).trimEnd()}...`;
  }
  return tmp;
}

function buildOnChange(setValue) {
  return (e) => setValue(e.currentTarget.value);
}

const allModels = [
  "gpt-3.5-turbo",
  "text-davinci-003",
  "text-davinci-002",
  "text-curie-001",
  "text-babbage-001",
  "text-ada-001",
  "gpt-4",
  "gpt-4-32k",
];

function MonoEmphasise({ children }) {
  return (
    <span className="inline-block rounded-sm bg-slate-300 px-[2px] font-mono text-gray-700">
      {children}
    </span>
  );
}

function Emphasise({ children }) {
  return (
    <span className="inline-block rounded-sm bg-slate-300 px-[2px] text-gray-700">
      {children}
    </span>
  );
}

function ReferenceLink({ href }) {
  return (
    <Button
      href={href}
      target="_blank"
      rel="noreferrer"
      appearance="softLink"
      small
      wrap
    >
      {href}
    </Button>
  );
}

function Pre({ children }) {
  return (
    <pre className="mb-1 whitespace-pre-wrap border-2 border-gray-300 p-1 text-xs">
      {children}
    </pre>
  );
}

const chatMessages = `[
  {
    "role": "system",
    "content": instruction
  },
  {
    "role": "user",
    "content": input
  }
]`;

function ResetButton(props) {
  return (
    <Button small variant="danger" appearance="box" {...props}>
      reset
    </Button>
  );
}

function Option({
  name,
  value,
  setValue,
  tooltip,
  defaultValue,
  textarea,
  password,
}) {
  const onChange = buildOnChange(setValue);
  return (
    <div className="flex flex-col justify-between gap-2">
      <div className="flex justify-between gap-2">
        <div className="flex items-center gap-2">
          <HeadingMedium>{name}</HeadingMedium>
          {tooltip}
        </div>
        {defaultValue !== undefined && (
          <ResetButton
            onClick={() => setValue(defaultValue)}
            disabled={value === defaultValue}
          />
        )}
      </div>
      {textarea ? (
        <Textarea rows={5} value={value} onChange={onChange} />
      ) : (
        <Input small value={value} onChange={onChange} password={password} />
      )}
    </div>
  );
}

function SettingsContent({ close, save }) {
  const {
    apiKey,
    setApiKey,
    model,
    setModel,
    maxTokensPerCluster,
    setMaxTokensPerCluster,
    topP,
    setTopP,
    temperature,
    setTemperature,
    labelInstruction,
    setLabelInstruction,
    frameInstruction,
    setFrameInstruction,
  } = useContext(SettingsContext);
  return (
    <div className="flex w-full flex-col overflow-hidden">
      <div className="z-20 flex flex-wrap items-center justify-between gap-6 border-b bg-slate-100 p-5">
        <div className="flex items-center gap-2">
          <ModalTitle>Cluster Label Generation Settings</ModalTitle>
          <QuestionTooltip place="right" clickable>
            These options are only required if you want to compute a label for
            each cluster.
          </QuestionTooltip>
        </div>
        <div className="flex items-center gap-2">
          <Button appearance="soft" variant="primary" onClick={close}>
            Close
          </Button>
          <Button appearance="fill" variant="success" onClick={save}>
            Save and Close
          </Button>
        </div>
      </div>
      <div className="grow space-y-4 overflow-y-auto p-5">
        <div className="list-inside list-disc text-sm text-slate-500">
          All options are stored in your browser&apos;s local storage. Options
          will be resetted to their default value when entering an empty value.
        </div>
        <div className="columns-1 gap-4 space-y-4 lg:columns-2">
          <div className="break-inside-avoid">
            <Card full>
              <CardHead>
                <HeadingSemiBig>Required</HeadingSemiBig>
              </CardHead>
              <CardContent>
                <div className="flex flex-col justify-between gap-2">
                  <Option
                    name="OpenAI Api Key"
                    tooltip={
                      <QuestionTooltip place="right" clickable>
                        This api key is distributed by OpenAI. It will never be
                        stored anywhere else than in the local store of your
                        browser and is sent to the api when requesting the
                        generation of cluster labels or media frames.
                        <div>
                          See:
                          <ul className="list-inside list-disc pl-2">
                            <li>
                              <ReferenceLink href="https://platform.openai.com/account/api-keys" />
                            </li>
                          </ul>
                        </div>
                      </QuestionTooltip>
                    }
                    value={apiKey}
                    setValue={setApiKey}
                    defaultValue={DEFAULTS.apiKey}
                    password
                  />
                </div>
                <div className="flex flex-col justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <HeadingMedium>Labeling Model</HeadingMedium>
                    <QuestionTooltip place="right" clickable>
                      Models prefixed with <MonoEmphasise>text-</MonoEmphasise>{" "}
                      are completion models and models prefixed with{" "}
                      <MonoEmphasise>gpt-</MonoEmphasise> are chat models.{" "}
                      <MonoEmphasise>gpt-3.5-turbo</MonoEmphasise> and{" "}
                      <MonoEmphasise>text-davinci-003</MonoEmphasise> have a
                      similar performance but{" "}
                      <MonoEmphasise>gpt-3.5-turbo</MonoEmphasise> is 10 times
                      cheaper. Read the help dialogs for the{" "}
                      <Emphasise>Instructions</Emphasise> option for more
                      information on how the prompts are built for the different
                      models.
                      <div>
                        See:
                        <ul className="list-inside list-disc pl-2">
                          <li>
                            <ReferenceLink href="https://platform.openai.com/docs/models" />
                          </li>
                          <li>
                            <ReferenceLink href="https://openai.com/pricing" />
                          </li>
                          <li>
                            <ReferenceLink href="https://platform.openai.com/docs/guides/completion" />
                          </li>
                          <li>
                            <ReferenceLink href="https://platform.openai.com/docs/guides/chat" />
                          </li>
                        </ul>
                      </div>
                    </QuestionTooltip>
                  </div>
                  <Categories
                    index={allModels.indexOf(model)}
                    onChange={(index) => {
                      setModel(index >= 0 ? allModels[index] : null);
                    }}
                    categories={allModels}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
          <div className="break-inside-avoid">
            <Card full>
              <CardHead>
                <div className="flex items-center gap-2">
                  <HeadingSemiBig>Instructions</HeadingSemiBig>
                  <QuestionTooltip place="left" clickable>
                    The instructions are used in the following template for
                    non-chat models:
                    <Pre>{'{instruction}\n\nInput: """{input}"""'}</Pre>
                    and in the following json for chat-models:
                    <Pre>{chatMessages}</Pre>
                    The <MonoEmphasise>input</MonoEmphasise> variable is
                    replaced by task-specific data (see the explanation for each
                    task).
                    <div>
                      See:
                      <ul className="list-inside list-disc pl-2">
                        <li>
                          <ReferenceLink href="https://platform.openai.com/docs/guides/completion" />
                        </li>
                        <li>
                          <ReferenceLink href="https://platform.openai.com/docs/guides/chat" />
                        </li>
                      </ul>
                    </div>
                  </QuestionTooltip>
                </div>
              </CardHead>
              <CardContent>
                <Option
                  name="Cluster Label Generation Instruction"
                  tooltip={
                    <QuestionTooltip place="left" clickable>
                      For this task, the <MonoEmphasise>input</MonoEmphasise>{" "}
                      variable in the template is replaced by the sentences from
                      the cluster ordered by their centrality. The list of
                      ordered sentences is discarded from the end to be smaller
                      than the value entered for the{" "}
                      <Emphasise>Max Tokens per Cluster</Emphasise> option.
                    </QuestionTooltip>
                  }
                  value={labelInstruction}
                  setValue={setLabelInstruction}
                  defaultValue={DEFAULTS.labelInstruction}
                  textarea
                />
                <Option
                  name="Media Frame Generation Instruction"
                  tooltip={
                    <QuestionTooltip place="left" clickable>
                      For this task, the <MonoEmphasise>input</MonoEmphasise>{" "}
                      variable in the template is replaced by the label that was
                      generated by cluster label generation step (see{" "}
                      <Emphasise>
                        Cluster Label Generation Instruction
                      </Emphasise>
                      )<Emphasise>Max Tokens per Cluster</Emphasise> option.
                    </QuestionTooltip>
                  }
                  value={frameInstruction}
                  setValue={setFrameInstruction}
                  defaultValue={DEFAULTS.frameInstruction}
                  textarea
                />
              </CardContent>
            </Card>
          </div>
          <div className="break-inside-avoid">
            <Card full>
              <CardHead>
                <HeadingSemiBig>Other</HeadingSemiBig>
              </CardHead>
              <CardContent>
                <Option
                  name="Max Tokens per Cluster"
                  tooltip={
                    <QuestionTooltip place="left">
                      This will limit the maximum number of tokens used per
                      cluster while computing the labels. When empty, the amount
                      of tokens is limited by the maximum input size of the
                      model (~4096). Use this option if you want limit the
                      amount of money spent for the labeling.
                    </QuestionTooltip>
                  }
                  value={maxTokensPerCluster}
                  setValue={setMaxTokensPerCluster}
                  defaultValue={DEFAULTS.maxTokensPerCluster}
                />
                <Option
                  name="Top p"
                  tooltip={
                    <QuestionTooltip place="left" clickable>
                      Only consider the highest ranked tokens that have a
                      combined probability mass less than this value.
                      <div>
                        See:
                        <ul className="list-inside list-disc pl-2">
                          <li>
                            <ReferenceLink href="https://platform.openai.com/docs/api-reference/completions/create#completions/create-top_p" />
                          </li>
                        </ul>
                      </div>
                    </QuestionTooltip>
                  }
                  value={topP}
                  setValue={setTopP}
                  defaultValue={DEFAULTS.topP}
                />
                <Option
                  name="Temperature"
                  tooltip={
                    <QuestionTooltip place="left" clickable>
                      The distribution of token probabilities will become more
                      uniformly distributed, when this value is increased. When
                      0, the generation will be deterministic.
                      <div>
                        See:
                        <ul className="list-inside list-disc pl-2">
                          <li>
                            <ReferenceLink href="https://platform.openai.com/docs/api-reference/completions/create#completions/create-temperature" />
                          </li>
                        </ul>
                      </div>
                    </QuestionTooltip>
                  }
                  value={temperature}
                  setValue={setTemperature}
                  defaultValue={DEFAULTS.temperature}
                />
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

function Settings({ close }) {
  const [settings, setTmpSettings] = useState(useContext(SettingsContext));
  const {
    apiKey,
    setApiKey,
    model,
    setModel,
    maxTokensPerCluster,
    setMaxTokensPerCluster,
    topP,
    setTopP,
    temperature,
    setTemperature,
    labelInstruction,
    setLabelInstruction,
    frameInstruction,
    setFrameInstruction,
  } = settings;

  const setTmpOption = (option) => (value) => {
    setTmpSettings((old) => ({ ...old, [option]: value }));
  };

  const currSettings = useMemo(
    () => ({
      apiKey,
      model,
      maxTokensPerCluster,
      topP,
      temperature,
      labelInstruction,
      frameInstruction,
      setApiKey: setTmpOption("apiKey"),
      setModel: setTmpOption("model"),
      setMaxTokensPerCluster: setTmpOption("maxTokensPerCluster"),
      setTopP: setTmpOption("topP"),
      setTemperature: setTmpOption("temperature"),
      setLabelInstruction: setTmpOption("labelInstruction"),
      setFrameInstruction: setTmpOption("frameInstruction"),
    }),
    [
      apiKey,
      maxTokensPerCluster,
      temperature,
      topP,
      model,
      labelInstruction,
      frameInstruction,
    ]
  );

  const save = () => {
    setApiKey(apiKey);
    setModel(model);
    setMaxTokensPerCluster(maxTokensPerCluster);
    setTopP(topP);
    setTemperature(temperature);
    setLabelInstruction(labelInstruction);
    setFrameInstruction(frameInstruction);
    close();
  };

  return (
    <SettingsContext.Provider value={currSettings}>
      <SettingsContent close={close} save={save} />
    </SettingsContext.Provider>
  );
}

function RedditURL({ url, cluster, labelModel }) {
  const {
    computeLabels,
    apiKey,
    model,
    maxTokensPerCluster,
    topP,
    temperature,
    labelInstruction,
    frameInstruction,
  } = useContext(SettingsContext);
  const getThread = useCallback(
    (signal) =>
      getThreadFromURL(
        url,
        computeLabels && defined(apiKey) && defined(model)
          ? {
              apiKey,
              model,
              maxTokensPerCluster,
              topP,
              temperature,
              directLabelInstruction: labelInstruction,
              directFrameInstruction: frameInstruction,
            }
          : {},
        signal
      ),
    [
      url,
      apiKey,
      model,
      maxTokensPerCluster,
      computeLabels,
      topP,
      temperature,
      labelInstruction,
      frameInstruction,
    ]
  );
  const { value, loading, error } = useAsync(getThread);
  const { pathname } = useLocation();
  if (loading) {
    return <CenterLoading message="fetching thread and computing clustering" />;
  }
  if (error) {
    return <GeneralError error={error} retryPath={pathname} />;
  }
  if (!value.success) {
    return <SuccessFalseError {...value} retryPath={pathname} />;
  }
  return (
    <Thread thread={value.data} labelModel={labelModel} cluster={cluster} />
  );
}

function RedditURLInput() {
  const navigate = useNavigate();
  const [url, setURL] = useState("");
  const [isOpen, openModal, closeModal] = useModal();
  const submit = () => {
    if (url) {
      navigate(`/from_url?url=${url}`);
    }
  };
  const {
    apiKey,
    model,
    maxTokensPerCluster,
    computeLabels,
    setComputeLabels,
    topP,
    temperature,
  } = useContext(SettingsContext);
  const requiredOptionsAreSet = defined(apiKey) && defined(model);
  const anyOptionIsSet =
    defined(apiKey) || defined(model) || Number.isInteger(maxTokensPerCluster);
  const lightText = !requiredOptionsAreSet || computeLabels;
  const successColor = lightText ? "text-green-600" : "text-green-400";
  const errorColor = lightText ? "text-red-600" : "text-red-400";
  return (
    <div className="grow overflow-auto pt-10 pb-20">
      <Container>
        <div className="flex flex-col pb-10">
          <div className="flex justify-center">
            <div className="max-w-[1000px] grow pb-4">
              <div className="flex w-full items-center justify-center gap-4">
                <div className="flex grow">
                  <div className="flex items-center whitespace-nowrap rounded-l-lg border-y-2 border-l-2 border-gray-600 bg-red-300 px-2">
                    Reddit URL
                  </div>
                  <Input
                    value={url}
                    onChange={(e) => setURL(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && submit()}
                    flatLeft
                    flatRight
                    bold
                  />
                  <button
                    type="button"
                    onClick={submit}
                    className="rounded-r-lg border-y-2 border-r-2 border-gray-600 bg-blue-500 px-2 text-white hover:bg-blue-700"
                  >
                    Submit
                  </button>
                </div>
                <div>
                  <FaCog
                    size={32}
                    onClick={openModal}
                    title="configure labeling"
                    className="cursor-pointer text-gray-400 hover:text-slate-600"
                  />
                  <Modal isOpen={isOpen} close={closeModal}>
                    <Settings close={closeModal} />
                  </Modal>
                </div>
                {requiredOptionsAreSet && (
                  <Checkbox
                    checked={computeLabels}
                    onChange={() => {
                      setComputeLabels((v) => !v);
                    }}
                    bold
                  >
                    <span className="text-base">Generate Summary</span>
                  </Checkbox>
                )}
              </div>
              <div
                className={`flex gap-4 text-xs ${
                  lightText ? "text-slate-900" : "text-slate-400"
                }`}
              >
                {anyOptionIsSet && (
                  <div className="flex flex-wrap gap-x-4">
                    {!requiredOptionsAreSet && (
                      <span>
                        <span className="font-bold">api-key:</span>{" "}
                        {apiKey ? (
                          <FaCheckCircle
                            className={`inline-block ${successColor}`}
                          />
                        ) : (
                          <FaExclamationCircle
                            className={`inline-block ${errorColor}`}
                          />
                        )}
                      </span>
                    )}
                    <span>
                      <span className="font-bold">model:</span>{" "}
                      {model ? (
                        <span>{model}</span>
                      ) : (
                        <FaExclamationCircle
                          className={`inline-block ${errorColor}`}
                        />
                      )}
                    </span>
                    {requiredOptionsAreSet && (
                      <>
                        <span>
                          <span className="font-bold">max tokens:</span>{" "}
                          {Number.isInteger(maxTokensPerCluster) ? (
                            <span>
                              {clipString(maxTokensPerCluster.toString())}
                            </span>
                          ) : (
                            <span>unlimited</span>
                          )}
                        </span>
                        <span>
                          <span className="font-bold">top p:</span>{" "}
                          <span>{parseFloat(topP.toFixed(3))}</span>
                        </span>
                        <span>
                          <span className="font-bold">temperature:</span>{" "}
                          <span>{parseFloat(temperature.toFixed(3))}</span>
                        </span>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
          <div
            className="text-center text-sm leading-7"
            style={{ overflowWrap: "anywhere" }}
          >
            <span>URL Format:</span>{" "}
            <span className="rounded-md bg-slate-200 p-[5px] pb-[3px] font-mono ring-2 ring-gray-400">
              https://www.reddit.com/r/changemyview/comments/12aalnu/cmv_all_drug_usage_and_possession_without_intent/
            </span>
          </div>
        </div>
        <StoredList />
      </Container>
    </div>
  );
}

function RedditURLParams() {
  const [searchParams] = useSearchParams();
  const url = searchParams.get("url");
  const labelModel = searchParams.get("labelModel");
  const frameModel = searchParams.get("frameModel");
  const cluster = searchParams.get("cluster");
  if (!url) return <RedditURLInput />;
  return (
    <RedditURL
      url={url}
      labelModel={labelModel}
      frameModel={frameModel}
      cluster={cluster}
    />
  );
}

export { RedditURLParams };
