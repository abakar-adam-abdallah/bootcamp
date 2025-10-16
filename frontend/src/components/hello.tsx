type Props = { name: string };
export default function Hello({ name }: Props) {
  return <h2>Bonjour, {name}</h2>;
}
