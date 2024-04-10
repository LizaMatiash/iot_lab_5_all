from ..entities.agent_data import AgentData
from ..entities.processed_agent_data import ProcessedAgentData


def process_agent_data(agent_data: AgentData) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    # get data from accelerometer
    height = agent_data.accelerometer.z

    # Road state
    if height <= 6000:
        road_state = "pothole"  # pothole, road is bad
    elif height > 5000 and height <= 16000:
        road_state = "smooth"  # smoth road, road is good
    else:
        road_state = "hump"  # hump, road is bad
    # Create an object that contains state of the road and iformation about the road
    processed_data_batch = ProcessedAgentData(
        road_state=road_state,
        agent_data=agent_data
    )

    return processed_data_batch
