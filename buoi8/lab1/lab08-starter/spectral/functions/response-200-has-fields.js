function resolveRef(schema, root, seenRefs) {
  if (!schema || typeof schema !== "object") return null;
  if (typeof schema.$ref !== "string") return schema;

  const ref = schema.$ref;
  if (!ref.startsWith("#/") || seenRefs.has(ref)) return null;

  let target = root;
  for (const part of ref.slice(2).split("/")) {
    const key = part.replace(/~1/g, "/").replace(/~0/g, "~");
    target = target?.[key];
    if (target === undefined) return null;
  }

  const nextRefs = new Set(seenRefs);
  nextRefs.add(ref);
  return resolveRef(target, root, nextRefs);
}

function hasFields(schema, root, seenRefs = new Set()) {
  const resolved = resolveRef(schema, root, seenRefs);
  if (!resolved || typeof resolved !== "object") return false;

  if (resolved.type === "array") {
    return hasFields(resolved.items, root, seenRefs);
  }

  if (
    resolved.properties &&
    typeof resolved.properties === "object" &&
    Object.keys(resolved.properties).length > 0
  ) {
    return true;
  }

  return ["allOf", "anyOf", "oneOf"].some(
    (composition) =>
      Array.isArray(resolved[composition]) &&
      resolved[composition].some((member) => hasFields(member, root, seenRefs)),
  );
}

module.exports = (schema, _options, context) => {
  if (hasFields(schema, context.document.data)) return;

  return [
    {
      message: "Response 200 schema must expose at least one field.",
    },
  ];
};
