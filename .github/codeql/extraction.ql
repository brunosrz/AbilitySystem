/** List extracted translation units and extraction failures for the CI gate. */
import cpp

from string kind, string detail
where
  exists(Compilation c |
    kind = "compiled" and detail = c.getAFileCompiled().getRelativePath()
  )
  or
  exists(Diagnostic d |
    d.getSeverity() >= 3 and kind = "error" and detail = d.getFullMessage()
  )
  or
  exists(Compilation c |
    not c.normalTermination() and
    kind = "error" and detail = "Extraction did not finish: " + c.getAFileCompiled().getRelativePath()
  )
select kind, detail
