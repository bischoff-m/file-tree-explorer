import { component$ } from "@builder.io/qwik";

export default component$(() => {
  return (
    <header class="h-full max-h-48">
      <button
        class="h-12 w-32 rounded bg-highlight"
        onClick$={async () => {
          console.log("Clicked");
        }}
      >
        Header Test
      </button>
    </header>
  );
});
