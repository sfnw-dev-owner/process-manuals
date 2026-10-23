-- Figures drawn from the model: a manual embeds one as
-- ![](model:<manual>/<figure>) or, in raw typst, as "model:<manual>/<figure>"
-- where an image path goes, e.g. `#fullpage("model:platform/step_03")`{=typst}.
-- render/model2svg.py renders each to SVG (cached in .rendered-figures/) and
-- this filter points the manual at it.

local dependencyMode = os.getenv("FIGURE_DEPS") ~= nil -- Set in ./go.

local PATTERN = "model:[%w_%-]+/[%w_%-%.]+"

-- The figures an element refers to.
local function refs(el)
   local found = {}
   if el.t == "Image" then
      if el.src:match("^" .. PATTERN .. "$") then
         table.insert(found, el.src)
      end
   elseif (el.t == "RawInline" or el.t == "RawBlock") and el.format == "typst" then
      for ref in el.text:gmatch('"(' .. PATTERN .. ')"') do
         table.insert(found, ref)
      end
   end
   return found
end

-- Ask model2svg.py (once per document) for the figures' SVGs, rendering any
-- that aren't cached. {ref: {svg = "/.rendered-figures/...", deps = {...}}}
local function resolve(doc)
   local wanted, seen = {}, {}
   local function collect(el)
      for _, ref in ipairs(refs(el)) do
         if not seen[ref] then
            seen[ref] = true
            table.insert(wanted, ref:sub(#"model:" + 1))
         end
      end
   end
   doc:walk({ Image = collect, RawInline = collect, RawBlock = collect })
   if #wanted == 0 then
      return {}
   end
   local args = { "/s/render/model2svg.py" }
   if dependencyMode then
      table.insert(args, "--deps")
   end
   for _, figure in ipairs(wanted) do
      table.insert(args, figure)
   end
   return pandoc.json.decode(pandoc.pipe("python3", args, ""), false)
end

-- Force Typst to consider a figure's sources dependencies (for the
-- last-revision date in ./go) without reading its SVG, which the dependency
-- pass doesn't render.
local emitted = {} -- each dependency once per document
local function dependencies(figures, found)
   local reads = {}
   for _, ref in ipairs(found) do
      for _, dep in ipairs(figures[ref:sub(#"model:" + 1)].deps) do
         if not emitted[dep] then
            emitted[dep] = true
            table.insert(reads, string.format("#let _ = read(%q, encoding: none)", dep))
         end
      end
   end
   return table.concat(reads, "\n") .. "\n"
end

function Pandoc(doc)
   if FORMAT ~= "typst" then
      return nil
   end
   local figures = resolve(doc)

   local function image(el)
      local found = refs(el)
      if #found == 0 then
         return nil
      end
      if dependencyMode then
         return pandoc.RawInline("typst", dependencies(figures, found))
      end
      el.src = "/s" .. figures[el.src:sub(#"model:" + 1)].svg
      return el
   end

   local function raw(el)
      local found = refs(el)
      if #found == 0 then
         return nil
      end
      if dependencyMode then
         el.text = dependencies(figures, found)
         return el
      end
      for _, ref in ipairs(found) do
         el.text = el.text:gsub('"' .. ref:gsub("%p", "%%%0") .. '"',
                                string.format("%q", figures[ref:sub(#"model:" + 1)].svg))
      end
      return el
   end

   return doc:walk({ Image = image, RawInline = raw, RawBlock = raw })
end
