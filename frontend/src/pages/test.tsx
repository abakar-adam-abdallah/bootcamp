import { Hello } from "../components/welto"; // accolades car export nommé

export default function Test() {
  return (
    <main style={{ padding: 16 }}>
      <h1>Mon App</h1>
      <Hello name="Adrianna" />
    </main>
  );
}
function MyButton() {
  return (
    <button>I'm a button</button>
  );
}

