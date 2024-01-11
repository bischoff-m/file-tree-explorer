import { component$, useContext, useSignal } from "@builder.io/qwik";
import { type FileTree } from "@prisma/client";
import { LuFile, LuFileQuestion, LuFolder } from "@qwikest/icons/lucide";
import prettyBytes from "pretty-bytes";
import { ExplorerContext } from "~/routes";

interface ExplorerListItemProps {
  file: FileTree;
}

function convertTime(time: Date | null) {
  if (time === null) return "";
  // DD.MM.YYYY HH:MM
  return (
    time.toLocaleDateString() + " " + time.toLocaleTimeString().slice(0, 5)
  );
}

function getIconFromType(type: string) {
  switch (type) {
    case "Directory":
      return <LuFolder class="inline-block h-6 w-6" />;
    case "File":
      return <LuFile class="inline-block h-6 w-6" />;
    default:
      return <LuFileQuestion class="inline-block h-6 w-6" />;
  }
}

export default component$<ExplorerListItemProps>((props) => {
  const explorerState = useContext(ExplorerContext);
  const isHovered = useSignal(false);

  return (
    <tr
      class="h-12 rounded bg-elements text-headline"
      style={{
        transform: isHovered.value ? "scale(1.02)" : "none",
        outline: isHovered.value ? "2px solid var(--headline)" : "none",
        boxShadow: isHovered.value ? "5px 5px 0 var(--headline)" : "none",
        transition: "all 0.1s ease-in-out",
        cursor: props.file.type === "Directory" ? "pointer" : "default",
      }}
      onMouseEnter$={() => {
        isHovered.value = true;
      }}
      onMouseLeave$={() => {
        isHovered.value = false;
      }}
      onClick$={() => {
        if (props.file.type === "Directory") {
          explorerState.currentPath = props.file.path;
        }
      }}
    >
      <td class="w-full font-bold">
        {getIconFromType(props.file.type)}
        <span class="ml-3">{props.file.name}</span>
      </td>
      <td>{convertTime(props.file.lastAccessTime)}</td>
      <td>{convertTime(props.file.lastWriteTime)}</td>
      <td>
        {prettyBytes(props.file.size, {
          maximumFractionDigits: 2,
          locale: "en-US",
        })}
      </td>
    </tr>
  );
});
