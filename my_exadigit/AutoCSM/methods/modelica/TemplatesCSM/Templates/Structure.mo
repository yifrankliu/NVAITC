within TemplatesCSM.Templates;
record Structure
  extends Icons.Structure;
  parameter Boolean useParallel=false "=true to use individual instances else assume single instance" annotation(Evaluate=true);
  parameter Integer n = 1 "# of instances" annotation(Evaluate=true);
  final parameter Integer n_int=if useParallel then 1 else n;
annotation(defaultComponentPrefixes ="parameter");
end Structure;
