import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import math


# ================================
#  FWA CONSTANTS
# ================================

@dataclass
class FWAConstants:
    pi: float = math.pi
    Lu: float = 1e-6  # люфт поля


# ================================
#  FIELD
# ================================

@dataclass
class FWAFIELD:
    id: str
    dimensions: int
    constants: FWAConstants
    meta: Dict[str, Any] = field(default_factory=dict)


# ================================
#  NODE
# ================================

@dataclass
class FWANode:
    id: str
    type: str
    position: List[float]
    state: str
    meta: Dict[str, Any] = field(default_factory=dict)


# ================================
#  WAVE
# ================================

@dataclass
class FWAWave:
    id: str
    source_node: str
    frequency: float
    amplitude: float
    phase: float
    meta: Dict[str, Any] = field(default_factory=dict)


# ================================
#  ERROR
# ================================

@dataclass
class FWAError:
    id: str
    type: str
    target_id: str
    severity: float
    meta: Dict[str, Any] = field(default_factory=dict)


# ================================
#  LINK
# ================================

@dataclass
class FWALink:
    id: str
    from_id: str
    to_id: str
    type: str
    meta: Dict[str, Any] = field(default_factory=dict)


# ================================
#  MODULE (FWA WORLD)
# ================================

@dataclass
class FWAModule:
    module_id: str
    version: str
    field: FWAFIELD
    nodes: List[FWANode] = field(default_factory=list)
    waves: List[FWAWave] = field(default_factory=list)
    errors: List[FWAError] = field(default_factory=list)
    links: List[FWALink] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    # ----------------------------
    # JSON EXPORT / IMPORT
    # ----------------------------

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=4)

    @staticmethod
    def from_json(data: str):
        raw = json.loads(data)

        field_obj = FWAFIELD(
            id=raw["field"]["id"],
            dimensions=raw["field"]["dimensions"],
            constants=FWAConstants(**raw["field"]["constants"]),
            meta=raw["field"].get("meta", {})
        )

        nodes = [FWANode(**n) for n in raw.get("nodes", [])]
        waves = [FWAWave(**w) for w in raw.get("waves", [])]
        errors = [FWAError(**e) for e in raw.get("errors", [])]
        links = [FWALink(**l) for l in raw.get("links", [])]

        return FWAModule(
            module_id=raw["module_id"],
            version=raw["version"],
            field=field_obj,
            nodes=nodes,
            waves=waves,
            errors=errors,
            links=links,
            meta=raw.get("meta", {})
        )


# ================================
#  FWA INTERPRETER (AI RUNTIME)
# ================================

class FWAInterpreter:

    def __init__(self, module: FWAModule):
        self.module = module
        self.node_map = {n.id: n for n in module.nodes}
        self.wave_map = {w.id: w for w in module.waves}

    # ---------------------------------
    #  GET NODE POSITION
    # ---------------------------------

    def get_position(self, node_id: str):
        return self.node_map[node_id].position

    # ---------------------------------
    #  SIMULATE WAVE PHASE SHIFT
    # ---------------------------------

    def update_wave_phase(self, wave_id: str, dt: float):
        wave = self.wave_map[wave_id]
        wave.phase += wave.frequency * dt
        wave.phase %= (2 * math.pi)

    # ---------------------------------
    #  APPLY ERROR TO NODE/WAVE
    # ---------------------------------

    def apply_error(self, error: FWAError):
        if error.target_id in self.node_map:
            node = self.node_map[error.target_id]
            node.state = "error"
            node.meta["severity"] = error.severity

        if error.target_id in self.wave_map:
            wave = self.wave_map[error.target_id]
            wave.amplitude *= (1.0 - error.severity)

    # ---------------------------------
    #  STEP SIMULATION
    # ---------------------------------

    def step(self, dt: float):
        for wave in self.module.waves:
            self.update_wave_phase(wave.id, dt)

        for err in self.module.errors:
            self.apply_error(err)


# ================================
#  EXAMPLE MODULE CREATION
# ================================

def create_minimal_fwa_module() -> FWAModule:
    constants = FWAConstants()

    field = FWAFIELD(
        id="FWA-Base",
        dimensions=3,
        constants=constants,
        meta={"description": "Base FWA field"}
    )

    node_zero = FWANode(
        id="N0",
        type="zero",
        position=[0.0, 0.0, 0.0],
        state="balanced"
    )

    node_source = FWANode(
        id="N1",
        type="wave-source",
        position=[1.0, 0.0, 0.0],
        state="active"
    )

    wave_1 = FWAWave(
        id="W1",
        source_node="N1",
        frequency=440.0,
        amplitude=1.0,
        phase=0.0
    )

    link_0_1 = FWALink(
        id="L0",
        from_id="N0",
        to_id="N1",
        type="field-connection"
    )

    module = FWAModule(
        module_id="FWA-Core-Example",
        version="3.0",
        field=field,
        nodes=[node_zero, node_source],
        waves=[wave_1],
        errors=[],
        links=[link_0_1],
        meta={"author": "Mark"}
    )

    return module


# ================================
#  MAIN (DEMO)
# ================================

if __name__ == "__main__":
    module = create_minimal_fwa_module()
    interpreter = FWAInterpreter(module)

    print("Initial module:")
    print(module.to_json())

    interpreter.step(0.01)

    print("\nAfter simulation step:")
    print(module.to_json())
