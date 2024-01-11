import { component$, useContext } from "@builder.io/qwik";
import ExplorerListItem from "~/components/ExplorerListItem";
import { ExplorerContext } from "~/routes";

export default component$(() => {
  const explorerState = useContext(ExplorerContext);

  return (
    <section class="flex-1 overflow-auto rounded-t bg-elements px-3 pt-3 text-headline">
      <style>
        {`
        table td:nth-child(4) {
          text-align: right;
        }
        table td, th {
          padding: 0 0.8rem;
        }
      `}
      </style>
      <table class="w-full table-auto border-separate border-spacing-1 whitespace-nowrap text-left">
        <thead>
          <tr class="h-7 align-top text-sm text-paragraph">
            <th>Name</th>
            <th>Last Access</th>
            <th>Last Write</th>
            <th>Size</th>
          </tr>
          <tr>
            <td colSpan={4}>
              <svg viewBox="0 0 1000 6" xmlns="http://www.w3.org/2000/svg">
                <line
                  x1="0"
                  y1="0"
                  x2="1000"
                  y2="0"
                  stroke-dasharray="3 6"
                  style={{ stroke: "var(--paragraph)", strokeWidth: 2 }}
                />
              </svg>
            </td>
          </tr>
        </thead>
        <tbody>
          {explorerState.nodes.map((file) => (
            <ExplorerListItem key={file.nodeID} file={file} />
          ))}
        </tbody>
      </table>
    </section>
  );
});
