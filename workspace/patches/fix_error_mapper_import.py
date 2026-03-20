# patch_purpose: fix_error_mapper_import

import sys
import os

try:
    # Add workspace to path to ensure capabilities can be imported
    workspace_path = os.path.join(os.path.dirname(__file__), 'workspace')
    if workspace_path not in sys.path:
        sys.path.insert(0, workspace_path)

    # Also add capabilities directory directly
    capabilities_path = os.path.join(workspace_path, 'capabilities')
    if capabilities_path not in sys.path:
        sys.path.insert(0, capabilities_path)
        
    # Ensure semantic error mapping capability can be imported
    semantic_capability_path = os.path.join(capabilities_path, 'semantic_error_mapping_capability')
    if semantic_capability_path not in sys.path:
        sys.path.insert(0, semantic_capability_path)
        
except Exception as e:
    pass