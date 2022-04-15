from .checkAlarms import CheckAlarms
from .checkCapabilities import CheckCapabilities
from .checkClusterSummary import CheckClusterSummary
from .checkConfigIssues import CheckConfigIssues
from .checkCpuPkg import CheckCpuPkg
from .checkDatastoreSummary import CheckDatastoreSummary
from .checkHardwareStatus import CheckHardwareStatus
from .checkHostSummary import CheckHostSummary
from .checkHostVMs import CheckHostVMs
from .checkLicences import CheckLicences
from .checkNetworkSummary import CheckNetworkSummary
from .checkPci import CheckPci
from .checkSensorInfo import CheckSensorInfo


CHECKS = {
    'CheckAlarms': CheckAlarms,
    'CheckCapabilities': CheckCapabilities,
    'CheckClusterSummary': CheckClusterSummary,
    'CheckConfigIssues': CheckConfigIssues,
    'CheckCpuPkg': CheckCpuPkg,
    'CheckDatastoreSummary': CheckDatastoreSummary,
    'CheckHardwareStatus': CheckHardwareStatus,
    'CheckHostSummary': CheckHostSummary,
    'CheckHostVMs': CheckHostVMs,
    'CheckLicences': CheckLicences,
    'CheckNetworkSummary': CheckNetworkSummary,
    'CheckPci': CheckPci,
    'CheckSensorInfo': CheckSensorInfo,
}
