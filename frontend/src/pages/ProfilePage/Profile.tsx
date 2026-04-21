import { useState, useEffect, useRef, type ChangeEvent } from "react";
import "./Profile.css";
import { Button, ProfileImg } from "@/shared";
import { LowerRank } from "@/shared";
import { StaticProfileImg } from "@/shared";
import type { Profile } from "./lib/profileInterface";
import { fetchProfileInfo } from "@/features/getProfileInfo/getProfileInfo";
import { useNavigate } from "react-router-dom";

export default function Profile() {
	const navigate = useNavigate();

	const [profile, setProfile] = useState<Profile | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const [currentImg, setCurrentImg] = useState<string>(ProfileImg);
	const fileInputRef = useRef<HTMLInputElement>(null);

	useEffect(() => {
		const controller = new AbortController();

		const loadProfile = async () => {
			try {
				setLoading(true);
				setError(null);

				const data = await fetchProfileInfo(controller.signal);
				setProfile(data);

				setCurrentImg((prev) => {
					if (prev.startsWith("blob:")) return prev;
					return data.avatarUrl || ProfileImg;
				});
			} catch (error) {
				if (error instanceof Error && error.name === "AbortError") {
					console.log("Abort Error");
					return;
				}

				if (
					error instanceof Error &&
					error.message === "Unauthorized"
				) {
					console.log("Unauthorized");
					navigate("/login", { replace: true });
					return;
				}

				setError("Failed to load profile information");
			} finally {
				setLoading(false);
			}
		};

		loadProfile();

		return () => {
			controller.abort();
		};
	}, [navigate]);

	useEffect(() => {
		return () => {
			if (currentImg.startsWith("blob:")) {
				URL.revokeObjectURL(currentImg);
			}
		};
	}, [currentImg]);

	const handleImgClick = () => {
		fileInputRef.current?.click();
	};

	const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0];
		if (!file) return;

		const allowedTypes = ["image/png", "image/jpeg"];
		if (!allowedTypes.includes(file.type)) {
			alert("Пожалуйста, выберите файл в формате PNG или JPG");
			e.target.value = "";
			return;
		}

		if (currentImg.startsWith("blob:")) {
			URL.revokeObjectURL(currentImg);
		}

		const newUrl = URL.createObjectURL(file);
		setCurrentImg(newUrl);
	};

	if (loading) {
		return <div>Loading...</div>;
	}

	if (error) {
		return <div>{error}</div>;
	}

	if (!profile) {
		return <div>No profile data</div>;
	}

	return (
		<div>
			<div className="profile-container flex box-light">
				<img
					className="profile-img"
					src={currentImg}
					alt="Profile Image"
					width={219}
					height={219}
					onClick={handleImgClick}
				/>

				<input
					type="file"
					accept="image/png, image/jpeg"
					ref={fileInputRef}
					onChange={handleFileChange}
					style={{ display: "none" }}
					data-testid="avatar-input"
				/>
				<div className="profile-right">
					<div className="flex profile-info-container">
						<span className="profile-info">{profile.username}</span>
						<span className="profile-info">Rank</span>
						<span className="profile-info">Streak</span>
					</div>
					<div className="profile-info-deeper flex-col">
						<span className="label">email:</span>
						<span className="value">{profile.email}</span>

						<span className="label">Member Since:</span>
						<span className="value">{profile.memberSince}</span>

						<span className="label">Last Seen:</span>
						<span className="value">{profile.lastSeen}</span>

						<span className="label">Now is online</span>
						<span className="value">
							{profile.isOnline ? "online" : "offline"}
						</span>
					</div>
				</div>
				<img
					src={StaticProfileImg}
					alt=""
					width={300}
					height={300}
					className="margin-static-profile-img"
				/>
				<button className="btn-settings-profile flex btn-ghost">
					Settings
				</button>
			</div>
			<div className="lower-profile-container flex box-light">
				<img
					src={LowerRank}
					alt="Rank"
					width={219}
					height={219}
					className="rank-profile"
				/>
				<div className="lower-profile-container-text profile-info-deeper">
					<div className="flex-col point-rank-container">
						<span className="margin-rank-profile">
							Points: {profile.points}
						</span>
						<span className="margin-point-to-next-rank">
							Points to next rank:
						</span>
					</div>
					<div className="flex margin-task-complete">
						<span>
							Task completed:
							<li>Easy: {profile.tasksCompleted.easy}</li>
							<li>Medium: {profile.tasksCompleted.medium}</li>
							<li>Hard: {profile.tasksCompleted.hard}</li>
						</span>
					</div>
					<span>
						Average grade:
						<li>Easy: {profile.averageGrade.easy}</li>
						<li>Medium: {profile.averageGrade.medium}</li>
						<li>Hard: {profile.averageGrade.hard}</li>
					</span>
				</div>
				<img
					src={StaticProfileImg}
					alt=""
					width={300}
					height={300}
					className="margin-static-profile-img"
				/>
			</div>
		</div>
	);
}
