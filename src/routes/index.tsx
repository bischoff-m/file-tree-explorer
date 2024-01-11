import {
  component$,
  createContextId,
  useContextProvider,
  useStore,
  useTask$,
  useVisibleTask$,
} from "@builder.io/qwik";
import { server$, type DocumentHead } from "@builder.io/qwik-city";
import { PrismaClient, type FileTree } from "@prisma/client";
import md5 from "md5";
import ExplorerControl from "~/components/ExplorerControl";
import ExplorerList from "~/components/ExplorerList";
import Header from "~/components/Header";

type ExplorerState = {
  currentPath: string | null;
  nodes: FileTree[];
};

const prisma = new PrismaClient();

export const ExplorerContext = createContextId<ExplorerState>("Explorer");

export default component$(() => {
  const explorerState = useStore<ExplorerState>({
    currentPath: null,
    nodes: [],
  });
  useContextProvider(ExplorerContext, explorerState);

  const getNodes = server$(async () => {
    // Get first 100 files in currentPath, ordered by name
    if (explorerState.currentPath === null) return [];
    return await prisma.fileTree.findMany({
      where: {
        parentID: md5(explorerState.currentPath),
      },
      orderBy: {
        name: "asc",
      },
      take: 100,
    });
  });

  // Set currentPath to root on first render
  useTask$(async () => {
    explorerState.currentPath = "C:\\";
  });

  // Update nodes when currentPath changes
  useVisibleTask$(async ({ track }) => {
    track(() => explorerState.currentPath);
    explorerState.nodes = await getNodes();
  });

  return (
    <>
      <div class="absolute flex h-full w-full justify-center overflow-hidden bg-main text-headline">
        <main class="ml-6 mr-6 flex w-full max-w-screen-lg flex-col gap-4">
          <Header />
          <ExplorerControl />
          <ExplorerList />
        </main>
      </div>
    </>
  );
});

export const head: DocumentHead = {
  title: "File Explorer",
  meta: [
    {
      name: "description",
      content: "Site description",
    },
  ],
};
